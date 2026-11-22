from rest_framework.routers import DefaultRouter

from .viewsets import ExampleMaterialViewSet, ExampleViewSet

router = DefaultRouter()
router.register("examples", ExampleViewSet, basename="example")
router.register("materials", ExampleMaterialViewSet, basename="material")
urlpatterns = router.urls
