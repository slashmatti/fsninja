# sensors/models.py
from django.db import models
from django.contrib.auth.models import User

class Sensor(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sensors"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    model = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.model})"
