# sensors/api.py
from datetime import datetime
from typing import List, Optional

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from ninja import Schema, Field
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from sensors.models import Sensor
from readings.models import Reading

# --- Schemas ---

class SensorCreateSchema(Schema):
    name: str = Field(..., example="Office Sensor A")
    model: str = Field(..., example="DHT22")
    description: Optional[str] = Field(None, example="Temperature sensor in office")

class SensorOutSchema(Schema):
    id: int
    name: str
    model: str
    description: Optional[str]

class PaginatedSensors(Schema):
    total: int
    page: int
    page_size: int
    results: List[SensorOutSchema]


@api_controller("/sensors", tags=["Sensors"], auth=JWTAuth())
class SensorController:

    @route.get("/", response=PaginatedSensors)
    def list_sensors(
        self, request, page: int = 1, page_size: int = 10, q: Optional[str] = None
    ):
        """
        List sensors owned by the current user.

        - **q**: Optional search term to match name or model.
        """
        sensors = Sensor.objects.filter(owner=request.auth)
        if q:
            sensors = sensors.filter(Q(name__icontains=q) | Q(model__icontains=q))

        paginator = Paginator(sensors, page_size)
        page_obj = paginator.get_page(page)

        return {
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "results": [SensorOutSchema.from_orm(s) for s in page_obj],
        }

    @route.post("/", response={201: SensorOutSchema})
    def create_sensor(self, request, payload: SensorCreateSchema):
        """
        Create a new sensor.
        """
        sensor = Sensor.objects.create(
            owner=request.auth,
            name=payload.name,
            model=payload.model,
            description=payload.description,
        )
        return 201, SensorOutSchema.from_orm(sensor)

    @route.get("/{sensor_id}/", response=SensorOutSchema)
    def get_sensor(self, request, sensor_id: int):
        """
        Retrieve details of a specific sensor.
        """
        sensor = get_object_or_404(Sensor, id=sensor_id, owner=request.auth)
        return SensorOutSchema.from_orm(sensor)

    @route.put("/{sensor_id}/", response=SensorOutSchema)
    def update_sensor(self, request, sensor_id: int, payload: SensorCreateSchema):
        """
        Update a sensor's details.
        """
        sensor = get_object_or_404(Sensor, id=sensor_id, owner=request.auth)
        sensor.name = payload.name
        sensor.model = payload.model
        sensor.description = payload.description
        sensor.save()
        return SensorOutSchema.from_orm(sensor)

    @route.delete("/{sensor_id}/", response={204: None})
    def delete_sensor(self, request, sensor_id: int):
        """
        Delete a sensor and cascade delete its readings.
        """
        sensor = get_object_or_404(Sensor, id=sensor_id, owner=request.auth)
        sensor.delete()
        return 204, None
