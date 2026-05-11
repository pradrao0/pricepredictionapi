from django.db import models
from django.contrib.auth.models import User

class HousePricePrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    total_sqft = models.FloatField()
    bath = models.IntegerField()
    bhk = models.IntegerField()
    location = models.CharField(max_length=100)

    predicted_price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} - {self.predicted_price}"