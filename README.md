# Smart City Big Data Analytics Platform

Production-style capstone project for ingesting IoT sensor data, streaming through Kafka, persisting in MongoDB, processing with Apache Spark (Docker), and visualizing via FastAPI + Streamlit.

## Architecture (Phase 1)

```text
Simulator → Kafka → Ingestion Consumer → MongoDB
                              ↓
                         Spark (Docker)
                              ↓
                          FastAPI → Streamlit Dashboard
```

**Important:** Spark runs entirely inside Docker. No Hadoop/HDFS, no host Java, and no Windows PySpark installation is required.

## Technology Stack

- Python 3.11
- FastAPI + Uvicorn
- Apache Kafka + Zookeeper
- MongoDB + Mongo Express
- Apache Spark / PySpark (Docker only)
- Streamlit + Plotly
- Docker Compose

## Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine + Compose (Linux)
- Git
- Optional: Python 3.11+ for local development outside Docker

## Quick Start

1. **Clone and configure environment**

   ```bash
   cp .env.example .env
   ```

   The default `.env` uses `localhost:9092` for host access and Docker Compose overrides internal service addresses automatically.

2. **Start all services**

   ```bash
   docker compose up -d --build
   ```

   Or:

   ```bash
   make up
   ```

3. **Verify health**

   ```bash
   curl http://localhost:8000/health
   make health
   ```

4. **Open interfaces**

   | Service | URL |
   |---------|-----|
   | API docs | http://localhost:8000/docs |
   | Dashboard | http://localhost:8501 |
   | Mongo Express | http://localhost:8081 |

## Docker Services

| Service | Purpose |
|---------|---------|
| `zookeeper` | Kafka coordination |
| `kafka` | Event streaming (`localhost:9092` host, `kafka:29092` internal) |
| `kafka-init` | One-shot topic creation |
| `mongodb` | Persistent storage |
| `mongo-express` | MongoDB admin UI |
| `spark` | PySpark analytics engine (Docker only) |
| `api` | FastAPI REST service |
| `dashboard` | Streamlit UI (calls API) |
| `consumer` | Kafka → MongoDB ingestion |
| `simulator` | Virtual IoT device data generator |

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Description |
|----------|-------------|
| `MONGO_URI` | MongoDB connection string (host profile) |
| `KAFKA_BOOTSTRAP` | Kafka bootstrap servers (host profile) |
| `KAFKA_BOOTSTRAP_INTERNAL` | Kafka address inside Docker (`kafka:29092`) |
| `KAFKA_SENSOR_TOPIC` | Primary sensor topic |
| `API_URL` | API URL used by dashboard |
| `ML_ENABLED` | ML module toggle (default `false`) |

Docker services override `MONGO_URI` and `KAFKA_BOOTSTRAP` for in-network communication.

## Commands

```bash
# Start
docker compose up -d --build

# Stop
docker compose down

# Logs
docker compose logs -f

# Service status
docker compose ps

# API health
curl http://localhost:8000/health
```

## Data Flow (Phase 1)

1. **Simulator** publishes JSON sensor events to Kafka topic `smartcity.sensor_data`.
2. **Consumer** validates events and stores raw records in MongoDB `sensor_data` collection.
3. **Spark container** keeps a local Spark session alive (analytics pipeline arrives in Phase 5).
4. **FastAPI** exposes `/health` with MongoDB and Kafka connectivity checks.
5. **Streamlit** displays platform health by calling the API.

## Legacy / Host Development

Existing modules under `backend/kafka/` remain available for manual host execution:

```bash
# Terminal 1 — simulator (host, uses localhost:9092 from .env)
python -m backend.simulator.main

# Terminal 2 — consumer (host)
python backend/kafka/consumer.py
```

The Docker `consumer` service uses `backend/ingestion/consumer_runner.py`, which preserves the same validation and repository logic.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Kafka connection refused from host | Ensure Docker is running; use `localhost:9092` on host |
| Kafka connection refused from container | Services must use `kafka:29092` (set automatically in Compose) |
| API health shows Kafka down | Wait for `kafka-init` to finish; check `docker compose logs kafka` |
| Spark unhealthy on first start | Allow up to 90s for JVM warmup; check `docker compose logs spark` |
| Mongo Express login | Use credentials from `.env` (`ME_CONFIG_BASICAUTH_*`) |

## Project Phases

- **Phase 1 (current):** Docker foundation, health endpoints, simulator + ingestion in Compose
- **Phase 2:** IoT data contract + validation
- **Phase 3:** Realistic simulator
- **Phase 4:** Ingestion hardening
- **Phase 5:** Spark analytics pipeline
- **Phase 6:** Alert engine
- **Phase 7:** ML (optional)
- **Phase 8–10:** Full API, dashboard pages, tests

## Hardware Integration (Future)

Physical ESP32 devices will publish the same JSON contract to Kafka via an edge gateway. Only the data source before Kafka changes; ingestion, storage, analytics, API, and dashboard remain unchanged.
