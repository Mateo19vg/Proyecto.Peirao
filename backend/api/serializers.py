from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Especie, Spot, Captura, Perfil


class EspecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = '__all__'


class SpotSerializer(serializers.ModelSerializer):
    # Indica al frontend si el usuario actual puede ver este spot (para el mapa del predictor)
    es_visible = serializers.SerializerMethodField()

    class Meta:
        model = Spot
        fields = '__all__'

    def get_es_visible(self, obj):
        # Spots globales (sin creador): siempre visibles
        if not obj.creador_id:
            return True
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        # El propio creador siempre ve sus spots
        if user and user.is_authenticated and obj.creador_id == user.id:
            return True
        # Spots de otro usuario: visibles solo si ese usuario tiene perfil público AND el usuario actual tiene perfil público
        if not user or not user.is_authenticated:
            return False
        try:
            perfil_propio = user.perfil
            if not perfil_propio.es_publico:
                return False
        except Perfil.DoesNotExist:
            return False

        perfil = getattr(obj.creador, 'perfil', None)
        return bool(perfil and perfil.es_publico)


class PerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Perfil
        fields = ['id', 'username', 'avatar', 'avatar_url', 'bio', 'mostrar_nombre', 'es_publico']
        extra_kwargs = {'avatar': {'write_only': True}}

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class CapturaSerializer(serializers.ModelSerializer):
    especie_nombre = serializers.CharField(source='especie.nombre', read_only=True)
    spot_nombre = serializers.CharField(source='spot.nombre', read_only=True)

    spot_latitud = serializers.FloatField(source='spot.latitud', read_only=True)
    spot_longitud = serializers.FloatField(source='spot.longitud', read_only=True)

    # Nombre público del pescador: respeta su preferencia de anonimato
    pescador_nombre = serializers.SerializerMethodField()
    pescador_avatar = serializers.SerializerMethodField()
    es_propia = serializers.SerializerMethodField()

    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Captura
        fields = '__all__'
        read_only_fields = ['usuario']

    def get_pescador_nombre(self, obj):
        if not obj.usuario:
            return "Pescador anónimo"
        perfil = getattr(obj.usuario, 'perfil', None)
        if perfil and not perfil.mostrar_nombre:
            return "Pescador anónimo"
        return obj.usuario.username

    def get_pescador_avatar(self, obj):
        if not obj.usuario:
            return None
        perfil = getattr(obj.usuario, 'perfil', None)
        if not perfil or not perfil.mostrar_nombre or not perfil.avatar:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(perfil.avatar.url) if request else perfil.avatar.url

    def get_es_propia(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and obj.usuario_id == user.id)

    def get_foto_url(self, obj):
        if obj.foto:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.foto.url) if request else obj.foto.url
        return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']