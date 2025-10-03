from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from ninja import Schema
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from ninja.pagination import paginate, PageNumberPagination

from sensors.models import Sensor
from readings.models import Reading

# ✅ Schemas
class ReadingIn(Schema):
    temperature: float
    humidity: float
    timestamp: datetime

class ReadingOut(Schema):
    id: int
    temperature: float
    humidity: float
    timestamp: datetime
    sensor_id: int

@api_controller("/sensors/{sensor_id}/readings", tags=["Readings"], auth=JWTAuth())
class ReadingController:
    """Endpoints for sensor readings"""

    @route.get("/", response=List[ReadingOut])
    @paginate(PageNumberPagination, page_size=50)
    def list_readings(
        self,
        sensor_id: int,
        timestamp_from: Optional[datetime] = None,
        timestamp_to: Optional[datetime] = None,
    ):
        """List readings (paginated), with optional time filters"""
        sensor = get_object_or_404(Sensor, id=sensor_id, owner=self.context.request.auth)
        qs = Reading.objects.filter(sensor=sensor)
        if timestamp_from:
            qs = qs.filter(timestamp__gte=timestamp_from)
        if timestamp_to:
            qs = qs.filter(timestamp__lte=timestamp_to)
        return qs.order_by("timestamp")

    @route.post("/", response=ReadingOut)
    def create_reading(self, sensor_id: int, payload: ReadingIn):
        """Create a new reading for a sensor"""
        sensor = get_object_or_404(Sensor, id=sensor_id, owner=self.context.request.auth)
        reading = Reading.objects.create(sensor=sensor, **payload.dict())
        return reading