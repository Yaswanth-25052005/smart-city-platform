import os

def _get_float_env(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default

# PROJECT/DEMO THRESHOLDS - NOT OFFICIAL REGULATORY LIMITS
THRESHOLD_AIR_QUALITY = _get_float_env("THRESHOLD_AIR_QUALITY", 150.0) # AQI
THRESHOLD_HIGH_TEMPERATURE = _get_float_env("THRESHOLD_HIGH_TEMPERATURE", 45.0) # Celsius
THRESHOLD_HIGH_NOISE = _get_float_env("THRESHOLD_HIGH_NOISE", 80.0) # dB
THRESHOLD_PARKING_CONGESTION = _get_float_env("THRESHOLD_PARKING_CONGESTION", 90.0) # Percentage

# Data Quality thresholds
THRESHOLD_TEMP_MIN = _get_float_env("THRESHOLD_TEMP_MIN", -20.0)
THRESHOLD_TEMP_MAX = _get_float_env("THRESHOLD_TEMP_MAX", 60.0)
