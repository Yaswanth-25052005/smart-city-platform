import time
from backend.simulator.device import VirtualESP32
from backend.kafka.producer import publish
from backend.config.settings import SIMULATOR_INTERVAL_SECONDS, SIMULATOR_DEVICE_COUNT

devices = [VirtualESP32(f"ESP32_{str(i+1).zfill(2)}") for i in range(SIMULATOR_DEVICE_COUNT)]

print(f"Starting Virtual Smart City with {SIMULATOR_DEVICE_COUNT} devices...\n")

if __name__ == "__main__":
    while True:
        for device in devices:
            data = device.read_sensor()
            publish(data)
            print(f"Sent: {data}")
            
        time.sleep(SIMULATOR_INTERVAL_SECONDS)