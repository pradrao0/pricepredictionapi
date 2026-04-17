from rest_framework import serializers
from .models import HousePricePrediction

class HousePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousePricePrediction
        fields = "__all__"
        read_only_fields = ["predicted_price", "created_at"]
