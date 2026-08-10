# backend/simulator/main.py

import time

from backend.simulator.device import VirtualESP32
from backend.kafka.producer import publish

devices = [

    VirtualESP32("ESP32_01"),

    VirtualESP32("ESP32_02"),

    VirtualESP32("ESP32_03"),

    VirtualESP32("ESP32_04"),

    VirtualESP32("ESP32_05")

]

print("Starting Virtual Smart City...\n")

while True:
    for device in devices:
        data = device.read_sensor()
        publish(data)
        print(f"Sent: {data}")

    time.sleep(3)