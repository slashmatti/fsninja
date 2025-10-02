# sensors/management/commands/seed_sensors.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from sensors.models import Sensor

SENSORS = [
    {"name": "device-001", "model": "EnviroSense"},
    {"name": "device-002", "model": "ClimaTrack"},
    {"name": "device-003", "model": "AeroMonitor"},
    {"name": "device-004", "model": "HydroTherm"},
    {"name": "device-005", "model": "EcoStat"},
]

class Command(BaseCommand):
    help = "Seed the database with 5 default sensors"

    def handle(self, *args, **options):
        User = get_user_model()
        owner = User.objects.first()
        if not owner:
            self.stdout.write(self.style.WARNING("⚠️ No users found. Create a user first."))
            return

        for s in SENSORS:
            sensor, created = Sensor.objects.get_or_create(
                name=s["name"], model=s["model"], owner=owner
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created {sensor.name}"))
            else:
                self.stdout.write(f"ℹ️ Sensor {sensor.name} already exists.")
