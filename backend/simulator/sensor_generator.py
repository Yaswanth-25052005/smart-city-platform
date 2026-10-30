import uuid
import random
from datetime import datetime, timezone
from backend.config.settings import SIMULATOR_ANOMALY_PROBABILITY

class SensorGenerator:
    def __init__(self, device_id):
        self.device_id = device_id
        
        locations = ["ZONE_A", "ZONE_B", "ZONE_C", "ZONE_D"]
        self.location_id = random.choice(locations)
        
        # Initial states
        self.temperature = round(random.uniform(20.0, 30.0), 2)
        self.humidity = round(random.uniform(40.0, 60.0), 2)
        self.air_quality = float(random.randint(50, 100))
        self.noise = round(random.uniform(35.0, 50.0), 2)
        
        self.parking_occupied = random.choice([True, False])
        self.streetlight_on = False

    def generate(self):
        current_time = datetime.now(timezone.utc)
        
        # Initialize defaults as None (null)
        temp, hum, aq, noise = None, None, None, None
        parking, streetlight = None, None

        if self.device_id == "ESP32_ENV_01":
            # 1. Temperature: gradual change +/- 0.5
            self.temperature += random.uniform(-0.5, 0.5)
            self.temperature = max(10.0, min(50.0, self.temperature))
            temp = round(self.temperature, 2)

            # 2. Humidity: gradual change +/- 1.0
            self.humidity += random.uniform(-1.0, 1.0)
            self.humidity = max(20.0, min(95.0, self.humidity))
            hum = round(self.humidity, 2)

            # 3. Air Quality: gradual +/- 2, occasional pollution anomaly
            if random.random() < SIMULATOR_ANOMALY_PROBABILITY:
                self.air_quality += random.uniform(50, 150)
            else:
                self.air_quality += random.uniform(-2, 2)
            self.air_quality = max(0.0, min(500.0, self.air_quality))
            aq = round(self.air_quality, 2)

            # 4. Noise: gradual +/- 1, occasional loud noise spike
            if random.random() < SIMULATOR_ANOMALY_PROBABILITY:
                self.noise += random.uniform(20, 40)
            else:
                self.noise += random.uniform(-1, 1)
                if self.noise > 60:
                    self.noise -= random.uniform(2, 5)
            self.noise = max(30.0, min(120.0, self.noise))
            noise = round(self.noise, 2)

        elif self.device_id == "ESP32_TRAFFIC_01":
            # 5. Parking: persist, but 5% chance to toggle
            if random.random() < 0.05:
                self.parking_occupied = not self.parking_occupied
            parking = self.parking_occupied

            # 6. Streetlight: day/night behavior (simulate night if time is between 18:00 and 06:00 UTC)
            hour = current_time.hour
            if hour >= 18 or hour < 6:
                self.streetlight_on = True
            else:
                self.streetlight_on = False
            streetlight = self.streetlight_on

        return {
            "event_id": str(uuid.uuid4()),
            "device_id": self.device_id,
            "location_id": self.location_id,
            "temperature": temp,
            "humidity": hum,
            "air_quality": aq,
            "noise": noise,
            "parking_occupied": parking,
            "streetlight_on": streetlight,
            "timestamp": current_time.isoformat()
        }