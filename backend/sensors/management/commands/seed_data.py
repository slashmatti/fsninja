# backend/sensors/management/commands/seed_data.py
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from sensors.models import Sensor
from readings.models import Reading

DEFAULT_CSV = "seed/sensor_readings_wide.csv"

SENSOR_SPECS = [
    ("device-001", "EnviroSense"),
    ("device-002", "ClimaTrack"),
    ("device-003", "AeroMonitor"),
    ("device-004", "HydroTherm"),
    ("device-005", "EcoStat"),
]

def parse_iso_timestamp(ts_raw: str):
    """Robust minimal ISO timestamp parsing (handles 'Z' -> +00:00)."""
    if ts_raw is None:
        raise ValueError("No timestamp provided")
    s = ts_raw.strip()
    if s.endswith("Z"):
        s = s.replace("Z", "+00:00")
    # Python's fromisoformat accepts 'YYYY-MM-DD HH:MM:SS+00:00' and 'T' variants.
    return datetime.fromisoformat(s)

class Command(BaseCommand):
    help = "Seed a test user, five sensors, and readings from a long-format CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            default=DEFAULT_CSV,
            help="Path to the CSV file (default: backend/seed/sensor_readings_wide.csv)",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="testuser",
            help="Username for the seeded test user",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="password123",
            help="Password for the seeded test user",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = options["csv"]
        username = options["username"]
        password = options["password"]

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return

        # 1) Create or get test user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created user: {username} / {password}"))
        else:
            self.stdout.write(self.style.NOTICE(f"ℹ️ User '{username}' already exists."))

        # 2) Create sensors for that user if missing
        sensors = {}
        for name, model in SENSOR_SPECS:
            sensor, _ = Sensor.objects.get_or_create(
                owner=user,
                name=name,
                defaults={"model": model},
            )
            sensors[name] = sensor
        self.stdout.write(self.style.SUCCESS("✅ Sensors created or verified."))

        # 3) Read CSV and create/update readings
        created_count = 0
        skipped_count = 0

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                device_id = (row.get("device_id") or "").strip()
                ts_raw = (row.get("timestamp") or "").strip()
                temp_raw = row.get("temperature")
                hum_raw = row.get("humidity")

                # Basic validation
                if not device_id or not ts_raw:
                    self.stdout.write(self.style.WARNING(f"⚠️ Skipping row with missing device_id or timestamp: {row}"))
                    skipped_count += 1
                    continue

                if device_id not in sensors:
                    self.stdout.write(self.style.WARNING(f"⚠️ Sensor '{device_id}' not found in seeded sensors - skipping row"))
                    skipped_count += 1
                    continue

                try:
                    timestamp = parse_iso_timestamp(ts_raw)
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f"⚠️ Could not parse timestamp '{ts_raw}': {exc} - skipping"))
                    skipped_count += 1
                    continue

                # Temperature/humidity may be empty; try to convert when available
                try:
                    temperature = None if temp_raw is None or str(temp_raw).strip() == "" else float(temp_raw)
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"⚠️ Invalid temperature '{temp_raw}' - skipping row"))
                    skipped_count += 1
                    continue

                try:
                    humidity = None if hum_raw is None or str(hum_raw).strip() == "" else float(hum_raw)
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"⚠️ Invalid humidity '{hum_raw}' - skipping row"))
                    skipped_count += 1
                    continue

                sensor = sensors[device_id]
                Reading.objects.update_or_create(
                    sensor=sensor,
                    timestamp=timestamp,
                    defaults={
                        "temperature": temperature,
                        "humidity": humidity,
                    },
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {created_count} readings."))
        if skipped_count:
            self.stdout.write(self.style.WARNING(f"⚠️ Skipped {skipped_count} invalid rows."))
        self.stdout.write(self.style.SUCCESS("🎉 Seeding complete."))
