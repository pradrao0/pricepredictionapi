from rest_framework import serializers
from .models import HousePricePrediction

class HousePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousePricePrediction
        fields = "__all__"
        read_only_fields = ["predicted_price", "created_at", "user"]

    # 🔥 Field-level validation
    def validate_total_sqft(self, value):
        if value <= 0:
            raise serializers.ValidationError("Square feet must be positive")
        return value

    def validate_bhk(self, value):
        if value <= 0:
            raise serializers.ValidationError("BHK must be positive")
        return value

    def validate_bath(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bathrooms must be positive")
        return value

    # 🔥 Object-level validation
    def validate(self, data):
        if data["bath"] > data["bhk"] + 2:
            raise serializers.ValidationError("Too many bathrooms for given BHK")
        return data