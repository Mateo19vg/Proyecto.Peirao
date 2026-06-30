from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import EspecieViewSet, SpotViewSet, CapturaViewSet, PerfilView, prediccion, register_user, ChatAsistenteView

router = DefaultRouter()
router.register(r'especies', EspecieViewSet, basename='especie')
router.register(r'spots', SpotViewSet, basename='spot')
router.register(r'capturas', CapturaViewSet, basename='captura')

urlpatterns = [
    path('', include(router.urls)),
    path('prediccion/', prediccion, name='prediccion'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_user, name='register'),

    # Perfil propio (GET/PUT) y perfil público de otro usuario (GET)
    path('perfil/', PerfilView.as_view(), name='perfil_propio'),
    path('perfil/<int:usuario_id>/', PerfilView.as_view(), name='perfil_publico'),
    path('chat/', ChatAsistenteView.as_view(), name='chat_asistente'),
]

# Endpoints reales de la API:
# GET            /api/especies/                          -> público
# POST/PUT/DEL   /api/especies/<id>/                      -> requiere login
# GET            /api/spots/                              -> público
# POST/PUT/DEL   /api/spots/<id>/                          -> requiere login
# GET            /api/capturas/                            -> público (feed de todos)
#                  ?especie=X&spot=Y&search=Z&usuario=N&mias=1
# POST           /api/capturas/                            -> requiere login
# PUT/DEL        /api/capturas/<id>/                       -> requiere login + ser el autor
# GET            /api/prediccion/?spot_id=X&especie_id=Y   -> público
# POST           /api/token/                               -> login
# POST           /api/token/refresh/                       -> refresh
# POST           /api/register/                            -> registro
# GET/PUT        /api/perfil/                               -> perfil propio
# GET            /api/perfil/<usuario_id>/                  -> perfil público de otro