import time
from backend.simulator.device import VirtualESP32
from backend.kafka.producer import publish
from backend.config.settings import SIMULATOR_INTERVAL_SECONDS

devices = [
    VirtualESP32("ESP32_ENV_01"),
    VirtualESP32("ESP32_TRAFFIC_01")
]

print("Starting Virtual Smart City with final hardware architecture (2 ESP32 nodes)...\n")

if __name__ == "__main__":
    while True:
        for device in devices:
            data = device.read_sensor()
            publish(data)
            print(f"Sent: {data}")
            
        time.sleep(SIMULATOR_INTERVAL_SECONDS)