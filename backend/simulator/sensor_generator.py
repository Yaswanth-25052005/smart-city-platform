# backend/simulator/sensor_generator.py

import random
from datetime import datetime


class SensorGenerator:

    @staticmethod
    def generate(device_id):

        import uuid
        from datetime import timezone

        locations = ["ZONE_A", "ZONE_B", "ZONE_C", "ZONE_D"]

        return {
            "event_id": str(uuid.uuid4()),
            "device_id": device_id,
            "location_id": random.choice(locations),
            "temperature": round(random.uniform(24, 38), 2),
            "humidity": round(random.uniform(40, 85), 2),
            "air_quality": float(random.randint(50, 220)),
            "noise": round(random.uniform(35, 90), 2),
            "parking_occupied": random.choice([True, False]),
            "streetlight_on": random.choice([True, False]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }