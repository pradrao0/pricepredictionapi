import pandas as pd
import joblib
import os

from django.conf import settings
from django.core.cache import cache

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import HousePricePrediction
from .serializers import HousePriceSerializer


# 📁 Paths (inside backend/)
MODEL_PATH = os.path.join(settings.BASE_DIR, "house_price_model.pkl")
LOCATIONS_PATH = os.path.join(settings.BASE_DIR, "locations.pkl")


# 🔁 Caching functions

def get_model():
    model = cache.get("ml_model")

    if model is None:
        model = joblib.load(MODEL_PATH)
        cache.set("ml_model", model, timeout=None)

    return model


def get_locations():
    locations = cache.get("locations")

    if locations is None:
        locations = joblib.load(LOCATIONS_PATH)
        cache.set("locations", locations, timeout=None)

    return locations


# 🚀 ViewSet

class HousePriceViewSet(ModelViewSet):
    queryset = HousePricePrediction.objects.all()
    serializer_class = HousePriceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 1️⃣ Save request data
        instance = serializer.save()

        # 2️⃣ Get cached model & locations
        model = get_model()
        locations = get_locations()

        # 3️⃣ Prepare ML input
        data = {
            "total_sqft": instance.total_sqft,
            "bath": instance.bath,
            "bhk": instance.bhk
        }

        for loc in locations:
            data[f"location_{loc}"] = 1 if instance.location == loc else 0

        X = pd.DataFrame([data])

        # 4️⃣ Predict
        predicted_price = model.predict(X)[0]

        # 5️⃣ Save prediction
        instance.predicted_price = predicted_price
        instance.save()