from django.db import models
from django.contrib.auth.models import User


class HousePricePrediction(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="house_predictions"
    )

    total_sqft = models.FloatField()

    bath = models.PositiveIntegerField()

    bhk = models.PositiveIntegerField()

    location = models.CharField(max_length=255)

    predicted_price = models.FloatField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.location} - "
            f"{self.predicted_price or 'Not Predicted'}"
        )