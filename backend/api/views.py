from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Especie, Spot, Captura
from .serializers import EspecieSerializer, SpotSerializer, CapturaSerializer
from .services import get_weather, calcular_puntuacion, describir_tiempo


# --- ViewSets CRUD estándar ---

class EspecieViewSet(viewsets.ModelViewSet):
    queryset = Especie.objects.all()
    serializer_class = EspecieSerializer


class SpotViewSet(viewsets.ModelViewSet):
    queryset = Spot.objects.all()
    serializer_class = SpotSerializer


class CapturaViewSet(viewsets.ModelViewSet):
    queryset = Captura.objects.all()
    serializer_class = CapturaSerializer

    def get_serializer_context(self):
        # Pasa el request al serializer para generar URLs absolutas de foto
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        especie_id = self.request.query_params.get('especie')
        spot_id = self.request.query_params.get('spot')
        search = self.request.query_params.get('search')
        if especie_id:
            qs = qs.filter(especie_id=especie_id)
        if spot_id:
            qs = qs.filter(spot_id=spot_id)
        if search:
            # Búsqueda en notas (icontains = case-insensitive)
            qs = qs.filter(notas__icontains=search)
        return qs


# --- Endpoint de predicción ---

@api_view(['GET'])
def prediccion(request):
    """
    GET /api/prediccion/?spot_id=1&especie_id=2
    Devuelve las condiciones actuales y una puntuación de pesca.
    """
    spot_id = request.query_params.get('spot_id')
    especie_id = request.query_params.get('especie_id')

    if not spot_id or not especie_id:
        return Response(
            {"error": "Se requieren spot_id y especie_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        spot = Spot.objects.get(pk=spot_id)
        especie = Especie.objects.get(pk=especie_id)
    except (Spot.DoesNotExist, Especie.DoesNotExist):
        return Response({"error": "Spot o especie no encontrados"}, status=404)

    # Llamar a Open-Meteo con las coordenadas del spot
    condiciones = get_weather(spot.latitud, spot.longitud)

    resultado = calcular_puntuacion(condiciones, especie)

    return Response({
        "spot": SpotSerializer(spot).data,
        "especie": EspecieSerializer(especie).data,
        "condiciones": condiciones,
        "descripcion_tiempo": describir_tiempo(
            condiciones.get("codigo_tiempo", 0) if condiciones else 0
        ),
        **resultado,  # puntuacion + resumen
    })
