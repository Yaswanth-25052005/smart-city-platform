import pytest
from uuid import uuid4
from datetime import datetime, timezone
from backend.domain.sensor import SensorEvent
from backend.services.validation_service import ValidationService
from pydantic import ValidationError

def test_valid_sensor_event():
    # 1. Valid SensorEvent
    data = {
        "event_id": str(uuid4()),
        "device_id": "ESP32_ENV_01",
        "location_id": "ZONE_A",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": 28.5,
        "humidity": 67.2,
        "air_quality": 92.0,
        "noise": 54.3,
        "parking_occupied": False,
        "streetlight_on": True
    }
    sensor = SensorEvent(**data)
    assert sensor.device_id == "ESP32_ENV_01"

def test_missing_event_id():
    # 2. Missing event_id
    data = {
        "device_id": "ESP32_ENV_01",
        "location_id": "ZONE_A",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    with pytest.raises(ValidationError) as exc:
        SensorEvent(**data)
    assert "event_id" in str(exc.value)

def test_invalid_uuid():
    # 3. Invalid UUID
    data = {
        "event_id": "not-a-uuid",
        "device_id": "ESP32_ENV_01",
        "location_id": "ZONE_A",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    with pytest.raises(ValidationError) as exc:
        SensorEvent(**data)
    assert "event_id" in str(exc.value)

def test_missing_device_id():
    # 4. Missing device_id
    data = {
        "event_id": str(uuid4()),
        "location_id": "ZONE_A",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    with pytest.raises(ValidationError) as exc:
        SensorEvent(**data)
    assert "device_id" in str(exc.value)

def test_missing_location_id():
    # 5. Missing location_id
    data = {
        "event_id": str(uuid4()),
        "device_id": "ESP32_ENV_01",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    with pytest.raises(ValidationError) as exc:
        SensorEvent(**data)
    assert "location_id" in str(exc.value)

def test_invalid_timestamp():
    # 6. Invalid timestamp
    data = {
        "event_id": str(uuid4()),
        "device_id": "ESP32_ENV_01",
        "location_id": "ZONE_A",
        "timestamp": "not-a-date"
    }
    with pytest.raises(ValidationError) as exc:
        SensorEvent(**data)
    assert "timestamp" in str(exc.value)

def test_nullable_sensor_values():
    # 7. Nullable sensor values
    data = {
        "event_id": str(uuid4()),
        "device_id": "ESP32_ENV_01",
        "location_id": "ZONE_A",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": None,
        "humidity": None
    }
    sensor = SensorEvent(**data)
    assert sensor.temperature is None
    assert sensor.noise is None

def test_invalid_numeric_values():
    # 8. Invalid numeric values
    data = {
        "event_id": str(uuid4()),
        "device_id": "ESP32_ENV_01",
        "location_id": "ZONE_A",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": "too_hot"
    }
    with pytest.raises(ValidationError) as exc:
        SensorEvent(**data)
    assert "temperature" in str(exc.value)

def test_invalid_boolean_values():
    # 9. Invalid boolean values
    data = {
        "event_id": str(uuid4()),
        "device_id": "ESP32_ENV_01",
        "location_id": "ZONE_A",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parking_occupied": "maybe"
    }
    with pytest.raises(ValidationError) as exc:
        SensorEvent(**data)
    assert "parking_occupied" in str(exc.value)

def test_simulator_generated_event():
    # 10. Simulator-generated event validation
    from backend.simulator.sensor_generator import SensorGenerator
    generator = SensorGenerator("ESP32_ENV_01")
    data = generator.generate()
    sensor = SensorEvent(**data)
    assert sensor.device_id == "ESP32_ENV_01"
    assert sensor.location_id in ["ZONE_A", "ZONE_B", "ZONE_C", "ZONE_D"]
    assert sensor.temperature is not None

def test_validation_service():
    # 11 & 12. Kafka serialization/deserialization & Consumer validation
    from backend.simulator.sensor_generator import SensorGenerator
    generator = SensorGenerator("ESP32_ENV_01")
    data = generator.generate()
    
    # Should not raise exception
    validated = ValidationService.validate(data)
    
    assert "event_id" in validated
    assert "timestamp" in validated
    assert isinstance(validated["event_id"], str)
    assert isinstance(validated["timestamp"], str)
    
    # Should raise error
    with pytest.raises(ValidationError):
        ValidationService.validate({})
