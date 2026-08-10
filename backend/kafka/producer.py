import json
from kafka import KafkaProducer
from backend.config.settings import KAFKA_BOOTSTRAP, TOPIC_NAME

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def publish(data):
    producer.send(TOPIC_NAME, data)
    producer.flush()