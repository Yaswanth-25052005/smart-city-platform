"""Kafka ingestion runner for containerized deployment."""

from backend.ingestion.consumer_runner import run_consumer

if __name__ == "__main__":
    run_consumer()
