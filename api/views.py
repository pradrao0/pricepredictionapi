import os
import logging

import pandas as pd
import joblib

from django.conf import settings
from django.core.cache import cache

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import HousePricePrediction
from .serializers import HousePriceSerializer


logger = logging.getLogger(__name__)


# -------------------------
# LOAD MODEL (CACHED)
# -------------------------
def get_model():
    model = cache.get("model")

    if model is None:
        model_path = os.path.join(
            settings.BASE_DIR,
            "api",
            "house_price_model.pkl"
        )

        model = joblib.load(model_path)
        cache.set("model", model, timeout=None)

    return model


# -------------------------
# LOAD LOCATIONS (CACHED)
# -------------------------
def get_locations():
    locations = cache.get("locations")

    if locations is None:
        location_path = os.path.join(
            settings.BASE_DIR,
            "api",
            "locations.pkl"
        )

        locations = joblib.load(location_path)
        cache.set("locations", locations, timeout=None)

    return locations


# -------------------------
# VIEWSET
# -------------------------
class HousePriceViewSet(ModelViewSet):

    serializer_class = HousePriceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ["location", "bhk", "bath"]
    search_fields = ["location"]
    ordering_fields = ["created_at", "predicted_price"]
    ordering = ["-created_at"]

    # -------------------------
    # USER ONLY DATA
    # -------------------------
    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return HousePricePrediction.objects.none()

        return HousePricePrediction.objects.filter(
            user=user
        ).order_by("-created_at")

    # -------------------------
    # CREATE + ML PREDICTION
    # -------------------------
    def perform_create(self, serializer):

        instance = serializer.save(user=self.request.user)

        try:
            model = get_model()
            locations = get_locations()

            # base features
            data = {
                "total_sqft": instance.total_sqft,
                "bath": instance.bath,
                "bhk": instance.bhk,
            }

            # one-hot encoding for location
            for loc in locations:
                data[f"location_{loc}"] = 1 if instance.location == loc else 0

            X = pd.DataFrame([data])

            logger.info(f"Model input: {X.to_dict()}")

            predicted_price = model.predict(X)[0]

            instance.predicted_price = round(float(predicted_price), 2)
            instance.save()

            logger.info(
                f"Prediction successful for user: {self.request.user.username}"
            )

        except Exception as e:
            logger.exception(
                f"Prediction FAILED for user {self.request.user.username}: {str(e)}"
            )

            instance.predicted_price = None
            instance.save()