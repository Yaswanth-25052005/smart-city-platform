from dotenv import load_dotenv
import os

load_dotenv()


def _get_env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    return value


# MongoDB
MONGO_URI = _get_env("MONGO_URI")
MONGO_DATABASE = _get_env("MONGO_DATABASE") or _get_env("DATABASE_NAME", "smart_city")
DATABASE_NAME = MONGO_DATABASE  # backward compatibility

# Kafka
KAFKA_BOOTSTRAP = _get_env("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_BOOTSTRAP_INTERNAL = _get_env("KAFKA_BOOTSTRAP_INTERNAL", "kafka:29092")
KAFKA_SENSOR_TOPIC = _get_env("KAFKA_SENSOR_TOPIC") or _get_env("TOPIC_NAME", "smartcity.sensor_data")
TOPIC_NAME = KAFKA_SENSOR_TOPIC  # backward compatibility
KAFKA_ALERT_TOPIC = _get_env("KAFKA_ALERT_TOPIC", "smartcity.alerts")
KAFKA_ANALYTICS_TOPIC = _get_env("KAFKA_ANALYTICS_TOPIC", "smartcity.analytics")

# API
API_HOST = _get_env("API_HOST", "0.0.0.0")
API_PORT = int(_get_env("API_PORT", "8000"))
API_URL = _get_env("API_URL", "http://localhost:8000")

# Dashboard
DASHBOARD_PORT = int(_get_env("DASHBOARD_PORT", "8501"))

# Simulator
SIMULATOR_INTERVAL_SECONDS = float(_get_env("SIMULATOR_INTERVAL_SECONDS", "3.0"))
SIMULATOR_DEVICE_COUNT = int(_get_env("SIMULATOR_DEVICE_COUNT", "5"))
SIMULATOR_ANOMALY_PROBABILITY = float(_get_env("SIMULATOR_ANOMALY_PROBABILITY", "0.05"))

# Spark (Docker only)
SPARK_MASTER = _get_env("SPARK_MASTER", "local[*]")
SPARK_APP_NAME = _get_env("SPARK_APP_NAME", "smart-city-analytics")

# Logging
LOG_LEVEL = _get_env("LOG_LEVEL", "INFO")

# ML (optional — Phase 7)
ML_ENABLED = _get_env("ML_ENABLED", "false").lower() in {"1", "true", "yes"}