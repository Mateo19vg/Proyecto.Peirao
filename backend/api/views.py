from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Especie, Spot, Captura, Perfil
from .serializers import EspecieSerializer, SpotSerializer, CapturaSerializer, PerfilSerializer
from .services import get_weather_range, calcular_puntuacion_rango


class EspecieViewSet(viewsets.ModelViewSet):
    queryset = Especie.objects.all()
    serializer_class = EspecieSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SpotViewSet(viewsets.ModelViewSet):
    queryset = Spot.objects.all()
    serializer_class = SpotSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CapturaViewSet(viewsets.ModelViewSet):
    """
    Todas las capturas son públicas: cualquiera (logueado o no) puede verlas.
    Crear, editar o borrar requiere estar autenticado, y solo sobre las propias.
    """
    serializer_class = CapturaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        # todas las capturas de todos los usuarios
        qs = Captura.objects.select_related('usuario', 'usuario__perfil', 'especie', 'spot').all()

        especie_id = self.request.query_params.get('especie')
        spot_id    = self.request.query_params.get('spot')
        search     = self.request.query_params.get('search')
        usuario_id = self.request.query_params.get('usuario')
        mias       = self.request.query_params.get('mias')  # "1" para ver solo las propias

        if especie_id:
            qs = qs.filter(especie_id=especie_id)
        if spot_id:
            qs = qs.filter(spot_id=spot_id)
        if search:
            qs = qs.filter(notas__icontains=search)
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)
        if mias == '1' and self.request.user.is_authenticated:
            qs = qs.filter(usuario=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.usuario_id != request.user.id:
            return Response({"error": "No puedes editar capturas de otro pescador."},
                             status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.usuario_id != request.user.id:
            return Response({"error": "No puedes borrar capturas de otro pescador."},
                             status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilView(APIView):
    """
    GET  /api/perfil/        -> perfil propio
    GET  /api/perfil/<id>/   -> perfil público de cualquier usuario
    PUT  /api/perfil/        -> editar el propio perfil (avatar, bio, mostrar_nombre)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, usuario_id=None):
        if usuario_id:
            perfil = get_object_or_404(Perfil, usuario_id=usuario_id)
        else:
            if not request.user.is_authenticated:
                return Response({"error": "No autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
            perfil = request.user.perfil
        return Response(PerfilSerializer(perfil, context={'request': request}).data)

    def put(self, request, usuario_id=None):
        if not request.user.is_authenticated:
            return Response({"error": "No autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
        perfil = request.user.perfil
        serializer = PerfilSerializer(perfil, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def prediccion(request):
    especie_id = request.query_params.get('especie_id')
    spot_id    = request.query_params.get('spot_id')
    lat_param  = request.query_params.get('lat')
    lon_param  = request.query_params.get('lon')

    if not especie_id:
        return Response({"error": "Falta el parámetro especie_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        especie = Especie.objects.get(pk=especie_id)
    except Especie.DoesNotExist:
        return Response({"error": "Especie no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if spot_id:
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Spot.DoesNotExist:
            return Response({"error": "Spot no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        lat, lon = spot.latitud, spot.longitud
        spot_data = SpotSerializer(spot).data
        nombre_ubicacion = spot.nombre

    elif lat_param and lon_param:
        try:
            lat = float(lat_param)
            lon = float(lon_param)
        except ValueError:
            return Response({"error": "lat y lon deben ser números"}, status=status.HTTP_400_BAD_REQUEST)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return Response({"error": "Coordenadas fuera de rango"}, status=status.HTTP_400_BAD_REQUEST)
        spot_data = None
        nombre_ubicacion = f"Punto personalizado ({lat:.4f}, {lon:.4f})"

    else:
        return Response(
            {"error": "Indica spot_id o las coordenadas lat y lon"},
            status=status.HTTP_400_BAD_REQUEST
        )

    condiciones_raw = get_weather_range(lat, lon)
    if not condiciones_raw:
        return Response(
            {"error": "No se pudieron obtener datos meteorológicos de Open-Meteo en este momento."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    timeline = calcular_puntuacion_rango(condiciones_raw, especie, lat=lat, lon=lon)

    return Response({
        "spot":             spot_data,
        "nombre_ubicacion": nombre_ubicacion,
        "lat":              lat,
        "lon":              lon,
        "especie":          EspecieSerializer(especie).data,
        "total_horas":      len(timeline),
        "timeline":         timeline
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response(
            {"error": "El nombre de usuario y la contraseña son campos obligatorios."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Este nombre de usuario ya está registrado en O Peirao."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # El Perfil se crea automáticamente vía signal post_save en models.py
    User.objects.create_user(username=username, password=password, email=email)

    return Response(
        {"message": "¡Pescador registrado con éxito!"},
        status=status.HTTP_201_CREATED
    )