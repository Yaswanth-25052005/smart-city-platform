
"""Forward ESP32 MQTT telemetry into the existing Kafka sensor topic."""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("mqtt-kafka-bridge")

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "smartcity/+/telemetry")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "smartcity.sensor_data")
CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "smartcity-mqtt-kafka-bridge")

ALLOWED_DEVICES = {"ESP32_ENV_01", "ESP32_TRAFFIC_01"}

producer = None


def make_producer():
    """Connect to Kafka, retrying while the broker is unavailable."""
    while True:
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda value: json.dumps(
                    value, separators=(",", ":")
                ).encode("utf-8"),
                retries=10,
                acks="all",
            )

            log.info(
                "Connected to Kafka at %s; topic=%s",
                KAFKA_BOOTSTRAP,
                KAFKA_TOPIC,
            )
            return kafka_producer

        except NoBrokersAvailable:
            log.warning("Kafka not ready; retrying in 3 seconds")
            time.sleep(3)


def number_or_none(data, *keys):
    """Return the first available numeric value, or None."""
    for key in keys:
        value = data.get(key)

        if value is None:
            continue

        # Do not accept booleans as numeric sensor readings.
        if isinstance(value, bool):
            log.warning("Ignoring boolean numeric field %s=%r", key, value)
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            log.warning("Ignoring non-numeric field %s=%r", key, value)
            return None

    return None


def bool_or_none(data, *keys):
    """Normalize supported boolean representations without guessing."""
    for key in keys:
        if key not in data or data[key] is None:
            continue

        value = data[key]

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)) and value in (0, 1):
            return bool(value)

        if isinstance(value, str):
            lowered = value.strip().lower()

            if lowered in ("true", "1", "yes", "on", "occupied", "detected"):
                return True

            if lowered in ("false", "0", "no", "off", "clear", "empty"):
                return False

        log.warning("Ignoring unrecognized boolean field %s=%r", key, value)
        return None

    return None


def normalize(payload, topic):
    """Convert MQTT telemetry into the canonical Kafka event."""
    if not isinstance(payload, dict):
        raise ValueError("MQTT payload must be a JSON object")

    # Identify the device from its MQTT topic.
    topic_parts = topic.split("/")
    topic_device = (
        topic_parts[1]
        if len(topic_parts) == 3 and topic_parts[0] == "smartcity"
        else None
    )

    device_id = str(
        payload.get("device_id") or topic_device or ""
    ).strip()

    if device_id not in ALLOWED_DEVICES:
        raise ValueError(
            f"Unknown device_id {device_id!r}; "
            f"expected one of {sorted(ALLOWED_DEVICES)}"
        )

    # Use supplied metadata when valid, otherwise create defaults.
    timestamp = payload.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp.strip():
        timestamp = datetime.now(timezone.utc).isoformat()

    location_id = str(
        payload.get("location_id")
        or ("ZONE_A" if device_id == "ESP32_ENV_01" else "ZONE_B")
    ).strip()

    event = {
        "event_id": str(payload.get("event_id") or uuid.uuid4()),
        "device_id": device_id,
        "location_id": location_id,
        "timestamp": timestamp,

        # Environmental telemetry.
        "temperature": number_or_none(
            payload, "temperature", "temperature_c"
        ),
        "humidity": number_or_none(
            payload, "humidity", "humidity_percent"
        ),
        # Raw ADC readings are provisional, not calibrated units.
        "air_quality": number_or_none(
            payload, "air_quality", "mq135_adc_raw"
        ),
        "noise": number_or_none(
            payload, "noise", "sound_raw"
        ),

        # Traffic telemetry: preserve every field independently.
        "ir_detected": bool_or_none(payload, "ir_detected"),
        "distance_cm": number_or_none(payload, "distance_cm"),
        "vehicle_detected": bool_or_none(payload, "vehicle_detected"),
        "parking_occupied": bool_or_none(payload, "parking_occupied"),
        "streetlight_on": bool_or_none(payload, "streetlight_on"),
    }

    # Preserve traffic signal state when supplied.
    traffic_signal = payload.get("traffic_signal")

    if traffic_signal is not None:
        if isinstance(traffic_signal, str) and traffic_signal.strip():
            event["traffic_signal"] = traffic_signal.strip().upper()
        else:
            log.warning(
                "Ignoring invalid traffic_signal=%r",
                traffic_signal,
            )

    # Remove missing sensor values, but retain required metadata.
    required_fields = {
        "event_id",
        "device_id",
        "location_id",
        "timestamp",
    }

    return {
        key: value
        for key, value in event.items()
        if value is not None or key in required_fields
    }


def on_connect(client, userdata, flags, reason_code, properties):
    """Subscribe to the configured telemetry topic after connecting."""
    if reason_code == 0:
        log.info(
            "Connected to MQTT broker %s:%s; subscribing %s",
            MQTT_HOST,
            MQTT_PORT,
            MQTT_TOPIC,
        )
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        log.error("MQTT connection failed: %s", reason_code)


def on_message(client, userdata, message):
    """Normalize and forward one MQTT message to Kafka."""
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        event = normalize(payload, message.topic)

        future = producer.send(KAFKA_TOPIC, value=event)
        future.get(timeout=10)

        log.info(
            "Forwarded %s from %s to Kafka (%s); fields=%s",
            event["device_id"],
            message.topic,
            KAFKA_TOPIC,
            sorted(event.keys()),
        )

    except Exception:
        log.exception(
            "Rejected or failed MQTT message on topic %s",
            message.topic,
        )


def main():
    global producer

    producer = make_producer()

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
    )
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            client.loop_forever(retry_first_connection=True)

        except Exception:
            log.exception(
                "MQTT bridge connection loop failed; retrying in 3 seconds"
            )
            time.sleep(3)


if __name__ == "__main__":
    main()
