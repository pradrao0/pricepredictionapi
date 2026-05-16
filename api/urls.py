from rest_framework.routers import DefaultRouter
from .views import HousePriceViewSet

router = DefaultRouter()

router.register(
    r"predictions",
    HousePriceViewSet,
    basename="predictions"
)

urlpatterns = router.urls