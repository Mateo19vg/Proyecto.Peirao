from rest_framework import serializers
from .models import Especie, Spot, Captura


class EspecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = '__all__'


class SpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spot
        fields = '__all__'


class CapturaSerializer(serializers.ModelSerializer):
    especie_nombre = serializers.CharField(source='especie.nombre', read_only=True)
    spot_nombre = serializers.CharField(source='spot.nombre', read_only=True)
    # Coordenadas del spot para el mapa del diario
    spot_latitud = serializers.FloatField(source='spot.latitud', read_only=True)
    spot_longitud = serializers.FloatField(source='spot.longitud', read_only=True)
    # Devuelve la URL completa de la foto (ej: http://localhost:8000/media/capturas/foto.jpg)
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Captura
        fields = '__all__'

    def get_foto_url(self, obj):
        if obj.foto:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.foto.url) if request else obj.foto.url
        return None


class PrediccionSerializer(serializers.Serializer):
    """Serializador de salida para el predictor. No mapea un modelo."""
    spot_id = serializers.IntegerField()
    especie_id = serializers.IntegerField()
    puntuacion = serializers.IntegerField(help_text="0-100, qué tan buenas son las condiciones")
    resumen = serializers.CharField()
    temperatura_agua = serializers.FloatField()
    velocidad_viento = serializers.FloatField()
    descripcion_tiempo = serializers.CharField()