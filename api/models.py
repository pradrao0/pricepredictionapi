from django.db import models





class HousePricePrediction(models.Model):
    total_sqft = models.FloatField()
    bath = models.IntegerField()
    bhk = models.IntegerField()
    location = models.CharField(max_length=100, default="Unknown")

    predicted_price = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction - {self.predicted_price}"
                            