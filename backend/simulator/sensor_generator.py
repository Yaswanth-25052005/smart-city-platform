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
        # 1. Temperature: gradual change +/- 0.5
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(10.0, min(50.0, self.temperature)) # bounds
        self.temperature = round(self.temperature, 2)

        # 2. Humidity: gradual change +/- 1.0
        self.humidity += random.uniform(-1.0, 1.0)
        self.humidity = max(20.0, min(95.0, self.humidity))
        self.humidity = round(self.humidity, 2)

        # 3. Air Quality: gradual +/- 2, occasional pollution anomaly
        if random.random() < SIMULATOR_ANOMALY_PROBABILITY:
            self.air_quality += random.uniform(50, 150) # Spike
        else:
            self.air_quality += random.uniform(-2, 2)
        self.air_quality = max(0.0, min(500.0, self.air_quality))
        self.air_quality = round(self.air_quality, 2)

        # 4. Noise: gradual +/- 1, occasional loud noise spike
        if random.random() < SIMULATOR_ANOMALY_PROBABILITY:
            self.noise += random.uniform(20, 40) # Spike
        else:
            self.noise += random.uniform(-1, 1)
            # Pull towards baseline if it spiked previously
            if self.noise > 60:
                self.noise -= random.uniform(2, 5)
        self.noise = max(30.0, min(120.0, self.noise))
        self.noise = round(self.noise, 2)

        # 5. Parking: persist, but 5% chance to toggle
        if random.random() < 0.05:
            self.parking_occupied = not self.parking_occupied

        # 6. Streetlight: day/night behavior (simulate night if time is between 18:00 and 06:00 UTC)
        current_time = datetime.now(timezone.utc)
        hour = current_time.hour
        if hour >= 18 or hour < 6:
            self.streetlight_on = True
        else:
            self.streetlight_on = False

        return {
            "event_id": str(uuid.uuid4()),
            "device_id": self.device_id,
            "location_id": self.location_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "air_quality": self.air_quality,
            "noise": self.noise,
            "parking_occupied": self.parking_occupied,
            "streetlight_on": self.streetlight_on,
            "timestamp": current_time.isoformat()
        }