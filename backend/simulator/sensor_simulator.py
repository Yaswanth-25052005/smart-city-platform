import time
from backend.simulator.device import VirtualESP32
from backend.config.settings import SIMULATOR_INTERVAL_SECONDS

class SensorSimulator:
    def __init__(self):
        self.device = VirtualESP32("ESP32_ENV_01")

    def generate_data(self):
        return self.device.read_sensor()

if __name__ == "__main__":
    simulator = SensorSimulator()
    while True:
        data = simulator.generate_data()
        print(data)
        time.sleep(SIMULATOR_INTERVAL_SECONDS)