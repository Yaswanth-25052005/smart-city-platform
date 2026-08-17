import pytest
from backend.simulator.sensor_generator import SensorGenerator
from backend.simulator.device import VirtualESP32
from backend.domain.sensor import SensorEvent

def test_sensor_generator_initial_state():
    generator = SensorGenerator("ESP32_TEST")
    assert generator.device_id == "ESP32_TEST"
    assert generator.location_id in ["ZONE_A", "ZONE_B", "ZONE_C", "ZONE_D"]
    assert 20.0 <= generator.temperature <= 30.0
    assert 40.0 <= generator.humidity <= 60.0
    assert 50.0 <= generator.air_quality <= 100.0
    assert 35.0 <= generator.noise <= 50.0

def test_sensor_generator_gradual_change():
    generator = SensorGenerator("ESP32_TEST")
    
    initial_temp = generator.temperature
    initial_hum = generator.humidity
    
    # Generate 1 step
    data = generator.generate()
    
    new_temp = generator.temperature
    new_hum = generator.humidity
    
    # Check bounded change
    assert abs(new_temp - initial_temp) <= 0.51
    assert abs(new_hum - initial_hum) <= 1.01
    
    # Validate against SensorEvent contract
    event = SensorEvent(**data)
    assert event.device_id == "ESP32_TEST"

def test_sensor_generator_bounds():
    generator = SensorGenerator("ESP32_TEST")
    # Force to limits
    generator.temperature = 49.8
    generator.humidity = 94.5
    
    for _ in range(10):
        generator.generate()
        
    assert generator.temperature <= 50.0
    assert generator.humidity <= 95.0

def test_virtual_esp32_device():
    device = VirtualESP32("ESP32_DEVICE")
    data = device.read_sensor()
    assert data["device_id"] == "ESP32_DEVICE"
    assert "event_id" in data
    assert "timestamp" in data
