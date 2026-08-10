import random
import time
from datetime import datetime


class SensorSimulator:

    def generate_data(self):

        import uuid
        from datetime import timezone
        return {
            "event_id": str(uuid.uuid4()),
            "device_id": "ESP32_01",
            "location_id": "ZONE_A",
            "temperature": round(random.uniform(25, 38), 2),
            "humidity": round(random.uniform(40, 90), 2),
            "air_quality": float(random.randint(50, 250)),
            "noise": round(random.uniform(30, 90), 2),
            "parking_occupied": random.choice([True, False]),
            "streetlight_on": random.choice([True, False]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


if __name__ == "__main__":

    simulator = SensorSimulator()

    while True:

        data = simulator.generate_data()

        print(data)

        time.sleep(5)