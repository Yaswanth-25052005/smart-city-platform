"""Shared application exceptions."""


class PlatformError(Exception):
    """Base exception for platform errors."""


class ConfigurationError(PlatformError):
    """Raised when required configuration is missing or invalid."""


class DatabaseConnectionError(PlatformError):
    """Raised when MongoDB is unreachable."""


class KafkaConnectionError(PlatformError):
    """Raised when Kafka is unreachable."""
