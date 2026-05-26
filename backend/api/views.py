from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Especie, Spot, Captura
from .serializers import EspecieSerializer, SpotSerializer, CapturaSerializer
from .services import get_weather, calcular_puntuacion, describir_tiempo


class EspecieViewSet(viewsets.ModelViewSet):
    queryset = Especie.objects.all()
    serializer_class = EspecieSerializer
    pagination_class = None


class SpotViewSet(viewsets.ModelViewSet):
    queryset = Spot.objects.all()
    serializer_class = SpotSerializer
    pagination_class = None


class CapturaViewSet(viewsets.ModelViewSet):
    queryset = Captura.objects.all()
    serializer_class = CapturaSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        especie_id = self.request.query_params.get('especie')
        spot_id    = self.request.query_params.get('spot')
        search     = self.request.query_params.get('search')
        if especie_id:
            qs = qs.filter(especie_id=especie_id)
        if spot_id:
            qs = qs.filter(spot_id=spot_id)
        if search:
            qs = qs.filter(notas__icontains=search)
        return qs


@api_view(['GET'])
def prediccion(request):
    spot_id    = request.query_params.get('spot_id')
    especie_id = request.query_params.get('especie_id')

    if not spot_id or not especie_id:
        return Response({"error": "Faltan parámetros spot_id y especie_id"}, status=400)

    try:
        spot    = Spot.objects.get(pk=spot_id)
        especie = Especie.objects.get(pk=especie_id)
    except (Spot.DoesNotExist, Especie.DoesNotExist):
        return Response({"error": "Spot o especie no encontrados"}, status=404)

    condiciones = get_weather(spot.latitud, spot.longitud)

    # Pasamos las coordenadas del spot para el cálculo de mareas
    resultado = calcular_puntuacion(
        condiciones, especie,
        lat=spot.latitud,
        lon=spot.longitud,
    )

    return Response({
        "spot":              SpotSerializer(spot).data,
        "especie":           EspecieSerializer(especie).data,
        "condiciones":       condiciones,
        "descripcion_tiempo": describir_tiempo(
            condiciones.get("codigo_tiempo", 0) if condiciones else 0
        ),
        "puntuacion":  resultado["puntuacion"],
        "resumen":     resultado["resumen"],
        "desglose":    resultado["desglose"],
        "luna":        resultado["luna"],
        "mareas":      resultado["mareas"],
    })