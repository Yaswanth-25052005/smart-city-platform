from backend.simulator.sensor_generator import SensorGenerator

class VirtualESP32:
    def __init__(self, device_id):
        self.device_id = device_id
        self.generator = SensorGenerator(device_id)

    def read_sensor(self):
        return self.generator.generate()