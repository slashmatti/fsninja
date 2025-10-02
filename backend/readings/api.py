# readings/api.py
from datetime import datetime
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Schema, Field
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from sensors.models import Sensor
from readings.models import Reading


# --- Schemas ---

class ReadingCreateSchema(Schema):
    temperature: float = Field(..., example=22.5)
    humidity: float = Field(..., example=55.2)
    timestamp: datetime = Field(..., example="2025-10-01T12:00:00Z")

class ReadingOutSchema(Schema):
    id: int
    temperature: float
    humidity: float
    timestamp: datetime


@api_controller("/sensors/{sensor_id}/readings", tags=["Readings"], auth=JWTAuth())
class ReadingController:

    @route.get("/", response=List[ReadingOutSchema])
    def list_readings(
        self,
        request,
        sensor_id: int,
        timestamp_from: Optional[datetime] = None,
        timestamp_to: Optional[datetime] = None,
    ):
        """
        List readings for a sensor, optionally filtered by timestamp range.
        """
        sensor = get_object_or_404(Sensor, id=sensor_id, owner=request.auth)

        qs = sensor.readings.all()
        if timestamp_from:
            qs = qs.filter(timestamp__gte=timestamp_from)
        if timestamp_to:
            qs = qs.filter(timestamp__lte=timestamp_to)

        return [ReadingOutSchema.from_orm(r) for r in qs.order_by("timestamp")]

    @route.post("/", response={201: ReadingOutSchema})
    def create_reading(self, request, sensor_id: int, payload: ReadingCreateSchema):
        """
        Create a new reading for a sensor.
        """
        sensor = get_object_or_404(Sensor, id=sensor_id, owner=request.auth)
        reading = Reading.objects.create(
            sensor=sensor,
            temperature=payload.temperature,
            humidity=payload.humidity,
            timestamp=payload.timestamp,
        )
        return 201, ReadingOutSchema.from_orm(reading)
