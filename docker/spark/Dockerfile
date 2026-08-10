FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY docker/spark/requirements-spark.txt ./requirements-spark.txt
RUN pip install --no-cache-dir -r requirements-spark.txt

COPY backend ./backend
COPY config ./config
COPY scripts ./scripts

CMD ["python", "backend/analytics/spark_daemon.py"]
