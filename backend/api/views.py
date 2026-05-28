from rest_framework import viewsets
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
    """
    Endpoint de prediccion. Acepta dos modos:
      - Spot guardado:  ?spot_id=X&especie_id=Y
      - Punto libre:    ?lat=42.3&lon=-8.7&especie_id=Y
    """
    especie_id = request.query_params.get('especie_id')
    spot_id    = request.query_params.get('spot_id')
    lat_param  = request.query_params.get('lat')
    lon_param  = request.query_params.get('lon')

    if not especie_id:
        return Response({"error": "Falta el parametro especie_id"}, status=400)

    try:
        especie = Especie.objects.get(pk=especie_id)
    except Especie.DoesNotExist:
        return Response({"error": "Especie no encontrada"}, status=404)

    # Modo 1: spot guardado
    if spot_id:
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Spot.DoesNotExist:
            return Response({"error": "Spot no encontrado"}, status=404)
        lat, lon = spot.latitud, spot.longitud
        spot_data = SpotSerializer(spot).data
        nombre_ubicacion = spot.nombre

    # Modo 2: coordenadas libres
    elif lat_param and lon_param:
        try:
            lat = float(lat_param)
            lon = float(lon_param)
        except ValueError:
            return Response({"error": "lat y lon deben ser numeros"}, status=400)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return Response({"error": "Coordenadas fuera de rango"}, status=400)
        spot_data = None
        nombre_ubicacion = f"Punto personalizado ({lat:.4f}, {lon:.4f})"

    else:
        return Response(
            {"error": "Indica spot_id o las coordenadas lat y lon"},
            status=400
        )

    condiciones = get_weather(lat, lon)
    resultado   = calcular_puntuacion(condiciones, especie, lat=lat, lon=lon)

    return Response({
        "spot":               spot_data,
        "nombre_ubicacion":   nombre_ubicacion,
        "lat":                lat,
        "lon":                lon,
        "especie":            EspecieSerializer(especie).data,
        "condiciones":        condiciones,
        "descripcion_tiempo": describir_tiempo(
            condiciones.get("codigo_tiempo", 0) if condiciones else 0
        ),
        "puntuacion":  resultado["puntuacion"],
        "resumen":     resultado["resumen"],
        "desglose":    resultado["desglose"],
        "luna":        resultado["luna"],
        "mareas":      resultado["mareas"],
    })