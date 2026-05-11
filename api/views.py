import pandas as pd
import joblib
import os

from django.conf import settings
from django.core.cache import cache

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import HousePricePrediction
from .serializers import HousePriceSerializer


# -------------------------
# CACHED MODEL
# -------------------------
def get_model():
    model = cache.get("model")

    if model is None:
        model_path = os.path.join(settings.BASE_DIR, 'api', 'house_price_model.pkl')
        model = joblib.load(model_path)
        cache.set("model", model, timeout=None)

    return model


# -------------------------
# CACHED LOCATIONS
# -------------------------
def get_locations():
    locations = cache.get("locations")

    if locations is None:
        location_path = os.path.join(settings.BASE_DIR, 'api', 'locations.pkl')
        locations = joblib.load(location_path)
        cache.set("locations", locations, timeout=None)

    return locations


# -------------------------
# VIEWSET
# -------------------------
class HousePriceViewSet(ModelViewSet):
    serializer_class = HousePriceSerializer
    permission_classes = [IsAuthenticated]

    # 🔥 REQUIRED FOR FILTERING TO WORK
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # FILTER / SEARCH / ORDER
    filterset_fields = ["location", "bhk", "bath"]
    search_fields = ["location"]
    ordering_fields = ["created_at", "predicted_price"]
    ordering = ["-created_at"]  # default ordering

    # USER-SPECIFIC DATA
    def get_queryset(self):
        return HousePricePrediction.objects.filter(user=self.request.user)

    # CREATE + PREDICT
    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)

        model = get_model()
        locations = get_locations()

        data = {
            "total_sqft": instance.total_sqft,
            "bath": instance.bath,
            "bhk": instance.bhk
        }

        for loc in locations:
            data[f"location_{loc}"] = 1 if instance.location == loc else 0

        X = pd.DataFrame([data])

        try:
            predicted_price = model.predict(X)[0]
        except Exception:
            predicted_price = None

        instance.predicted_price = predicted_price
        instance.save()