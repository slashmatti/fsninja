# readings/management/commands/load_readings.py
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from sensors.models import Sensor
from readings.models import Reading
from django.db import transaction

class Command(BaseCommand):
    help = "Load sensor readings from a long-format CSV file with columns: timestamp, device_id, temperature, humidity"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file")

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        self.stdout.write(f"📥 Loading readings from {csv_path}...")

        created_count = 0
        skipped_count = 0

        with open(csv_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                device_id = row.get("device_id")
                timestamp_raw = row.get("timestamp")
                temp = row.get("temperature")
                humidity = row.get("humidity")

                if not (device_id and timestamp_raw and temp and humidity):
                    self.stdout.write(self.style.WARNING(f"⚠️ Skipping row with missing data: {row}"))
                    skipped_count += 1
                    continue

                try:
                    sensor = Sensor.objects.get(name=device_id)
                except Sensor.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"⚠️ Sensor '{device_id}' not found. Skipping."))
                    skipped_count += 1
                    continue

                timestamp = datetime.fromisoformat(timestamp_raw)

                Reading.objects.update_or_create(
                    sensor=sensor,
                    timestamp=timestamp,
                    defaults={
                        "temperature": float(temp),
                        "humidity": float(humidity),
                    },
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Done. Imported or updated {created_count} readings."))
        if skipped_count:
            self.stdout.write(self.style.WARNING(f"⚠️ Skipped {skipped_count} rows."))
