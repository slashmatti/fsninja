# sensors/api.py
from typing import List, Optional
from django.db.models import Q
from ninja import Schema
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from ninja.pagination import paginate, PageNumberPagination

from sensors.models import Sensor

# ✅ Pydantic schemas
class SensorIn(Schema):
    name: str
    model: str
    description: Optional[str] = None

class SensorOut(Schema):
    id: int
    name: str
    model: str
    description: Optional[str]
    owner_id: int

@api_controller("/sensors", tags=["Sensors"], auth=JWTAuth())
class SensorController:
    """Endpoints for managing sensors"""

    @route.get("/", response=List[SensorOut])
    @paginate(PageNumberPagination, page_size=10)
    def list_sensors(self, request, q: Optional[str] = None):
        """List sensors (paginated). Supports ?q=search by name/model."""
        sensors = Sensor.objects.filter(owner=request.auth)
        if q:
            sensors = sensors.filter(Q(name__icontains=q) | Q(model__icontains=q))
        return sensors.order_by("id")

    @route.post("/", response=SensorOut)
    def create_sensor(self, request, payload: SensorIn):
        """Create a new sensor"""
        sensor = Sensor.objects.create(owner=request.auth, **payload.dict())
        return sensor

    @route.get("/{sensor_id}/", response=SensorOut)
    def get_sensor(self, request, sensor_id: int):
        """Get details of a sensor"""
        return Sensor.objects.get(id=sensor_id, owner=request.auth)

    @route.put("/{sensor_id}/", response=SensorOut)
    def update_sensor(self, request, sensor_id: int, payload: SensorIn):
        """Update a sensor"""
        sensor = Sensor.objects.get(id=sensor_id, owner=request.auth)
        for field, value in payload.dict().items():
            setattr(sensor, field, value)
        sensor.save()
        return sensor

    @route.delete("/{sensor_id}/", response={204: None})
    def delete_sensor(self, request, sensor_id: int):
        """Delete a sensor (cascade deletes readings)"""
        sensor = Sensor.objects.get(id=sensor_id, owner=request.auth)
        sensor.delete()
        return 204, None
