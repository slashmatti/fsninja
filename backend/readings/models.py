# readings/models.py
from django.db import models
from sensors.models import Sensor

class Reading(models.Model):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="readings"
    )
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["sensor", "timestamp"]),
        ]
        unique_together = ("sensor", "timestamp")

    def __str__(self):
        return f"{self.sensor.name} @ {self.timestamp}"
