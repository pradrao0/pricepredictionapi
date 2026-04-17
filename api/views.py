import pandas as pd
import joblib
import os

from django.conf import settings
from django.core.cache import cache

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from .models import HousePricePrediction
from .serializers import HousePriceSerializer


def get_model():
    model_path = os.path.join(settings.BASE_DIR, 'api', 'house_price_model.pkl')
    print("MODEL PATH:", model_path)   
    return joblib.load(model_path)

def get_locations():
    location_path = os.path.join(settings.BASE_DIR, 'api', 'locations.pkl')
    print("LOCATION PATH:", location_path)   
    return joblib.load(location_path)


def get_locations():
    locations = cache.get("locations")

    if locations is None:
        locations = joblib.load(LOCATIONS_PATH)
        cache.set("locations", locations, timeout=None)

    return locations


#  ViewSet

class HousePriceViewSet(ModelViewSet):
    queryset = HousePricePrediction.objects.all()
    serializer_class = HousePriceSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Save request data
        instance = serializer.save()

        #  Get cached model & locations
        model = get_model()
        locations = get_locations()

        #  Prepare ML input
        data = {
            "total_sqft": instance.total_sqft,
            "bath": instance.bath,
            "bhk": instance.bhk
        }

        for loc in locations:
            data[f"location_{loc}"] = 1 if instance.location == loc else 0

        X = pd.DataFrame([data])

        # Predict
        predicted_price = model.predict(X)[0]

        # Save prediction
        instance.predicted_price = predicted_price
        instance.save()