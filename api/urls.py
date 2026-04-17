from rest_framework.routers import DefaultRouter
from .views import HousePriceViewSet

router = DefaultRouter()
router.register("predict", HousePriceViewSet, basename="predict")

urlpatterns = router.urls
