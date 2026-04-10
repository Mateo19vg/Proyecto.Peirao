from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EspecieViewSet, SpotViewSet, CapturaViewSet, prediccion

router = DefaultRouter()
router.register(r'especies', EspecieViewSet)
router.register(r'spots', SpotViewSet)
router.register(r'capturas', CapturaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('prediccion/', prediccion, name='prediccion'),
]

# Endpoints generados automáticamente por el router:
# GET/POST   /api/especies/
# GET/PUT/DELETE /api/especies/<id>/
# GET/POST   /api/spots/
# GET/POST   /api/capturas/
# GET        /api/prediccion/?spot_id=1&especie_id=2
