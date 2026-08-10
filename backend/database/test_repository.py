from datetime import datetime

from backend.database.repository import SensorRepository

sample = {
    "event_id": "123e4567-e89b-12d3-a456-426614174000",
    "device_id": "ESP32_01",
    "location_id": "ZONE_A",
    "temperature": 30.5,
    "humidity": 61,
    "air_quality": 145,
    "noise": 52,
    "parking_occupied": True,
    "streetlight_on": False,
    "timestamp": datetime.now()
}

SensorRepository.insert_sensor_data(sample)

print("Inserted Successfully")

print(SensorRepository.get_latest())