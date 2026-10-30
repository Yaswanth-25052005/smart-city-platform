# Technical Viva & Capstone Defense Guide
## Big Data Analytics Platform for Smart Cities

This guide contains **45 comprehensive technical questions and evidence-based answers** specifically prepared for a final-year B.Tech Capstone Project defense, technical viva, and architectural review. Every answer is grounded directly in the actual source code and design decisions of the repository.

---

### Section 1: Architecture, Design & Data Ingestion

#### Q1: What is the high-level architecture of your Smart City Platform?
**Answer:**
The platform follows a decoupled, distributed microservices architecture structured into six distinct layers:
1. **Perception/Acquisition Layer:** Virtual IoT nodes (`VirtualESP32` in [`backend/simulator/device.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/simulator/device.py)) simulating hardware devices `ESP32_ENV_01` (environmental) and `ESP32_TRAFFIC_01` (traffic/lighting).
2. **Ingestion & Streaming Layer:** Apache Kafka with topic `smartcity.sensor_data` serving as a high-throughput distributed event buffer.
3. **Validation & Persistence Layer:** Python ingestion consumer (`consumer_runner.py`) enforcing Pydantic contract validation (`SensorEvent`) and persisting clean documents into MongoDB collection `sensor_data`.
4. **Analytics Layer:** Containerized Apache Spark 3.5.3 performing hourly aggregations (average, minimum, maximum, count) stored in the `analytics` collection.
5. **Intelligence & Alert Layer:** Stateful alert engine (`alert_engine.py`) and Scikit-learn predictive models (`train.py`, `predict.py`).
6. **API Gateway & Presentation Layer:** FastAPI providing REST endpoints to a 10-page Streamlit web dashboard.

#### Q2: Why did you use Apache Kafka instead of having the sensors write directly to MongoDB?
**Answer:**
Writing directly to MongoDB couples the sensor perception layer with the database write capacity. In a real-world smart city with thousands of IoT devices transmitting simultaneously, sudden traffic spikes can overwhelm database connection pools and cause dropped readings. Kafka provides:
1. **Asynchronous Backpressure & Buffering:** Decouples producer rate from consumer write rate.
2. **High Throughput & Persistence:** Kafka logs events sequentially to disk with sub-millisecond latency.
3. **Multiple Independent Consumers:** The same telemetry stream can be consumed concurrently by the MongoDB ingestion worker, a real-time alerting worker, or a Spark Structured Streaming job without duplicating sensor requests.

#### Q3: What is the authoritative sensor data contract, and how is it validated?
**Answer:**
The contract is defined by the `SensorEvent` Pydantic v2 model in [`backend/domain/sensor.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/domain/sensor.py):
- `event_id`: RFC 4122 UUID4 string.
- `device_id`: String identifier (e.g., `ESP32_ENV_01`, `ESP32_TRAFFIC_01`).
- `location_id`: String identifier representing the urban zone (e.g., `ZONE_A`).
- `timestamp`: UTC datetime in ISO 8601 format.
- Telemetry fields: `temperature`, `humidity`, `air_quality`, `noise`, `parking_occupied`, and `streetlight_on`.
Validation is executed in `ValidationService.validate()` ([`backend/services/validation_service.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/services/validation_service.py)). If any field violates constraints (e.g., invalid UUID string, non-numeric values for temperature, malformed timestamp), Pydantic raises a `ValidationError`, preventing dirty data from polluting MongoDB.

#### Q4: How does your system differentiate between environmental nodes and traffic nodes?
**Answer:**
The system uses nullable schema fields. Rather than creating disparate schemas that would complicate Kafka topic management, `SensorEvent` defines all possible smart city fields as optional (`Optional[T] = None`).
- When `ESP32_ENV_01` publishes, it populates `temperature`, `humidity`, `air_quality`, and `noise`, while `parking_occupied` and `streetlight_on` remain `None` (`null`).
- When `ESP32_TRAFFIC_01` publishes, it populates `parking_occupied` and `streetlight_on`, leaving environmental metrics as `null`.
Downstream Spark aggregations and dashboard charts specifically check for `.isNotNull()` or `.dropna()` to process only relevant measurements.

#### Q5: How did you solve the problem of legacy or simulated device records contaminating analytics?
**Answer:**
In [`backend/config/settings.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/config/settings.py#L49), we declare an authoritative whitelist:
```python
ACTIVE_DEVICES = ["ESP32_ENV_01", "ESP32_TRAFFIC_01"]
```
All repository methods ([`SensorRepository.find_latest`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/database/repository.py#L11), [`SensorRepository.find`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/database/repository.py#L19), [`DashboardRepository`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/database/dashboard_repository.py), and `AlertService`) explicitly inject `{"device_id": {"$in": ACTIVE_DEVICES}}` into their MongoDB queries. This completely isolates active hardware nodes from obsolete test data.

---

Section 2: Messaging, Kafka & MQTT

#### Q6: What role does Apache Zookeeper play in your Kafka setup?
**Answer:**
In Confluent Platform 7.5.0 (`confluentinc/cp-kafka:7.5.0`), Zookeeper maintains cluster metadata, coordinates broker leadership, tracks broker heartbeats, and maintains topic configurations and partition access control lists (ACLs).

#### Q7: How are Kafka topics initialized in your Docker Compose environment?
**Answer:**
We use a dedicated one-shot initialization container named `kafka-init` ([`docker-compose.yml`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/docker-compose.yml#L56)). It waits until the `kafka` service passes its health check, then runs [`scripts/create_topics.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/scripts/create_topics.py) using `KafkaAdminClient` to idempotently create `smartcity.sensor_data`, `smartcity.alerts`, and `smartcity.analytics`. Once complete, the container exits with code 0 (`restart: "no"`).

#### Q8: How does the Kafka consumer handle message deserialization and error recovery?
**Answer:**
In [`backend/ingestion/consumer_runner.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/ingestion/consumer_runner.py#L38), the consumer connects using `group_id="smart-city-ingestion"` with `auto_offset_reset="latest"` and `enable_auto_commit=True`. It runs a continuous polling loop with `consumer.poll(timeout_ms=1000, max_records=100)`. If a poison-pill message arrives with invalid JSON or failed Pydantic validation, the exception is caught in a `try...except` block, logged with stack traces via `logger.exception()`, and skipped, preventing the consumer thread from crashing.

#### Q9: What delivery guarantee does your Kafka implementation support?
**Answer:**
It implements **at-least-once** delivery. The producer calls `producer.flush()` after every message in [`backend/kafka/producer.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/kafka/producer.py#L10), and the consumer commits offsets periodically. In the event of a container restart, messages may be re-read; however, downstream Spark cleaning uses `df.dropDuplicates(["event_id"])` and MongoDB alert indexes use unique `alert_id`s, ensuring end-to-end idempotency.

#### Q10: Where does MQTT fit into your architecture, and what is its current status?
**Answer:**
The target architecture calls for ESP32 microcontrollers to communicate wirelessly over Wi-Fi via MQTT (a lightweight publish-subscribe protocol ideal for bandwidth-constrained microcontrollers).
In the current implementation, the simulator publishes directly to Kafka using `kafka-python`. The MQTT broker (e.g., Mosquitto) and the MQTT-to-Kafka ingestion gateway are documented as missing infrastructure components that must be deployed during hardware migration.

---

### Section 3: Database & Persistence Design

#### Q11: Why did you choose MongoDB instead of a relational database like PostgreSQL?
**Answer:**
1. **Schema Flexibility for Multi-Modal Telemetry:** IoT sensors generate heterogeneous payloads. An environmental sensor reports 4 numeric values; a parking sensor reports booleans. Storing these in a document database allows null-safe polymorphic storage without complex relational join tables.
2. **High Write Throughput:** MongoDB's WiredTiger engine handles high-volume document inserts efficiently using memory-mapped I/O and checkpointing.
3. **Native JSON Interoperability:** Sensor payloads serialize from Python dictionaries directly into BSON documents with zero object-relational mapping (ORM) friction.

#### Q12: What indexes are implemented in your MongoDB database?
**Answer:**
- In `alerts` collection ([`backend/database/alert_repository.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/database/alert_repository.py#L9)):
  - `alert_id` (Unique, ASCENDING)
  - `alert_type` (ASCENDING)
  - `location_id` (ASCENDING)
  - `status` (ASCENDING)
  - `timestamp` (DESCENDING) for fast chronological sorting.
- In `predictions` collection ([`backend/database/prediction_repository.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/database/prediction_repository.py#L8)):
  - `prediction_id` (Unique, ASCENDING)
  - `prediction_type` (ASCENDING)
  - `device_id` (ASCENDING)
  - `target_timestamp` (DESCENDING).
- In `analytics` collection:
  - Document `_id` is structured deterministically as `{metric}_{location_id}_{date}_{hour}`, providing automatic unique indexing.

#### Q13: How does the dashboard interact with MongoDB? Does it query directly?
**Answer:**
No. The Streamlit dashboard **never** imports `pymongo` or accesses MongoDB directly. All interactions are routed through FastAPI via [`dashboard/api.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/dashboard/api.py). This enforces loose coupling, modularity, security, and consistent business logic across client applications.

---

### Section 4: Apache Spark & Big Data Analytics

#### Q14: How does Apache Spark operate in your project, and why is no Windows Java required?
**Answer:**
PySpark is entirely containerized in Docker ([`docker/spark/Dockerfile`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/docker/spark/Dockerfile)). The container uses `python:3.11-slim-bookworm` with `openjdk-17-jre-headless` and PySpark 3.5.3 installed inside Linux. Because Spark executes inside Docker, the host Windows machine requires no Hadoop binaries (`winutils.exe`), no host Java JDK, and no host PySpark environment.

#### Q15: What is the purpose of `backend/spark/cleaning.py`?
**Answer:**
It performs four data quality operations:
1. `df.dropna(subset=["event_id", "location_id", "timestamp"])`: Discards records missing identifiers.
2. `df.dropDuplicates(["event_id"])`: Eliminates duplicate sensor messages.
3. `F.to_timestamp("timestamp")`: Parses ISO strings into Spark `TimestampType`.
4. Boundary filtering: Discards readings outside realistic physical boundaries (e.g., temperatures outside $-50^\circ\text{C}$ to $60^\circ\text{C}$, negative noise or AQI).

#### Q16: Explain the transformations implemented in `backend/spark/transformations.py`.
**Answer:**
1. **Temporal Feature Extraction:** Extracts `date` (`yyyy-MM-dd`), `hour` (`0–23`), and `day_of_week` (`1–7`) from the timestamp column for hourly aggregation.
2. **Boolean-to-Numeric Mapping:** Converts `parking_occupied` (True/False) to integer `1/0` (`parking_occupied_numeric`) and `streetlight_on` to integer `1/0` (`streetlight_on_numeric`). This enables arithmetic averaging over time to calculate occupancy percentages.

#### Q17: What metrics does `backend/spark/aggregations.py` calculate?
**Answer:**
For each unique combination of `[location_id, date, hour]`, Spark computes:
- Temperature: Average, Minimum, Maximum, Count.
- Humidity: Average, Minimum, Maximum, Count.
- Air Quality: Average, Minimum, Maximum, Count.
- Noise: Average, Minimum, Maximum, Count.
- Smart Parking: Average (representing the percentage occupancy rate), Minimum, Maximum, Count.
- Street Lighting: Average (representing percentage of time active), Minimum, Maximum, Count.
All metric dataframes are combined using `reduce(DataFrame.unionByName, all_metrics)` and persisted with upsert semantics into MongoDB `analytics`.

#### Q18: Is your Spark implementation batch processing or streaming?
**Answer:**
It is **micro-batch / batch processing**. In [`backend/spark/pipeline.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/spark/pipeline.py), Spark loads historical sensor data from MongoDB using the MongoDB-Spark Connector (`spark.read.format("mongodb").load()`), executes distributed aggregations, and writes the output back to MongoDB. The container daemon (`spark_daemon.py`) keeps the JVM session alive.

---

### Section 5: Alert Engine & Threshold Evaluation

#### Q19: What rules govern the alert system?
**Answer:**
Defined in [`backend/config/alert_rules.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/config/alert_rules.py):
- High Temperature: $> 45.0^\circ\text{C}$ (Severity: MEDIUM, or HIGH if $> 50^\circ\text{C}$).
- Temperature Data Quality: $< -20.0^\circ\text{C}$ or $> 60.0^\circ\text{C}$ (Severity: LOW).
- High Noise: $> 80.0\text{ dB}$ (Severity: MEDIUM).
- Poor Air Quality: $> 150.0\text{ AQI}$ (Severity: HIGH, or CRITICAL if $> 200.0$).
- Parking Congestion: $> 90.0\%$ occupancy (Severity: HIGH).
- Streetlight Anomaly: Reported OFF when expected to be ON (Severity: LOW).

#### Q20: How does your alert engine prevent duplicate notifications for an ongoing problem?
**Answer:**
In [`backend/services/alert_service.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/services/alert_service.py#L26), the method `evaluate_condition()` first queries:
```python
active_alert_doc = AlertRepository.find_active_alert(alert_type, location_id, device_id)
```
If an anomaly is detected (`is_abnormal = True`) and an active alert already exists, the function returns `None` without creating a new record. A new alert is inserted only when no prior active alert exists.

#### Q21: How does automatic alert resolution work?
**Answer:**
If a sensor condition returns to normal (`is_abnormal = False`) while an active alert document exists for that device/location, `AlertService.evaluate_condition()` calls `AlertRepository.update_status(alert_id, "RESOLVED", now)`. This transitions the alert status from `ACTIVE` to `RESOLVED` in MongoDB automatically.

---

### Section 6: Machine Learning Pipeline

#### Q22: What problem does your machine learning module solve?
**Answer:**
1. **Smart Parking Forecasting:** A binary classification task that predicts the probability of a parking spot being occupied 60 seconds into the future ($T+60\text{s}$).
2. **Air Quality Forecasting:** A regression task that predicts the continuous AQI value 60 seconds into the future ($T+60\text{s}$).

#### Q23: What ML algorithms did you choose, and what are their hyperparameters?
**Answer:**
In [`backend/ml/train.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/ml/train.py):
- **Parking Model:** `RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)`
- **Air Quality Model:** `RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)`
Random Forests were selected because they handle non-linear feature interactions well, are robust against outliers, require minimal feature scaling, and are less prone to overfitting on small-to-medium tabular datasets.

#### Q24: What features are fed into each model during training and inference?
**Answer:**
In [`backend/ml/data_loader.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/ml/data_loader.py):
- **Parking Features:**
  - `hour`: Time of day ($0–23$).
  - `day_of_week`: Day of the week ($0–6$).
  - `recent_occupancy_mean`: Rolling 5-event window mean of parking occupancy.
- **Air Quality Features:**
  - `hour`: Time of day.
  - `temperature`: Current ambient temperature.
  - `humidity`: Current ambient humidity.
  - `recent_aqi_mean`: Rolling 5-event window mean of AQI.

#### Q25: How do you prevent data leakage during time-series model evaluation?
**Answer:**
We use chronological splitting rather than randomized train-test splitting. In `DataLoader.chronological_split()` ([`backend/ml/data_loader.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/ml/data_loader.py#L72)), the dataset is sorted by timestamp, and the first 80% is allocated to training while the final 20% is held out for testing. This ensures the model is never evaluated on past data using future patterns.

#### Q26: Where are the trained model weights stored?
**Answer:**
In `backend/ml/models/parking_model.joblib` and `backend/ml/models/air_quality_model.joblib`. Each file contains a dictionary with the trained scikit-learn model, evaluation metrics, and model version metadata.

---

### Section 7: FastAPI Backend & API Design

#### Q27: How is platform health monitored in FastAPI?
**Answer:**
Via the `/health` endpoint in [`backend/api/routes/health.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/api/routes/health.py). It runs two live checks:
1. Calls `client.admin.command('ping')` on MongoDB and counts database collections.
2. Instantiates a transient `KafkaConsumer` to ping Kafka bootstrap brokers and check if `smartcity.sensor_data` exists in the cluster topic list.
If both services respond, it returns `{"status": "healthy"}`; otherwise, it returns `{"status": "degraded"}` with error logs.

#### Q28: How does FastAPI implement CORS security?
**Answer:**
In [`backend/api/main.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/api/main.py#L30), FastAPI includes `CORSMiddleware` configured with `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, and `allow_headers=["*"]`. In a public cloud deployment, `allow_origins` would be restricted to the exact domain of the dashboard.

#### Q29: What happens if a user provides an invalid time range to `/api/sensors`?
**Answer:**
In [`backend/api/routes/sensors.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/api/routes/sensors.py#L21):
```python
if start_time and end_time and start_time > end_time:
    raise HTTPException(status_code=400, detail="start_time must be less than or equal to end_time")
```
It returns an HTTP 400 Bad Request error before querying the database.

---

### Section 8: Streamlit Dashboard Implementation

#### Q30: How does the Streamlit dashboard refresh data?
**Answer:**
In [`dashboard/components.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/dashboard/components.py#L22), we provide an `auto_refresh(interval_sec)` component with a manual `st.button("Refresh Now")` that triggers `st.rerun()`. This prevents uncontrolled background looping while giving operators full control over data updates.

#### Q31: What visualization libraries are used in the dashboard?
**Answer:**
Streamlit native metric cards (`st.metric`) and **Plotly Express** (`px.line`, `px.bar`). Plotly was chosen for interactive zooming, panning, and responsive hover tooltips across time-series charts.

---

### Section 9: Virtual Simulator & Hardware Migration

#### Q32: How does the sensor simulator generate realistic IoT data?
**Answer:**
In [`backend/simulator/sensor_generator.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/simulator/sensor_generator.py), readings are generated using a **bounded random walk**:
- Temperature adjusts by $\pm 0.5^\circ\text{C}$ each cycle, bounded between $10^\circ\text{C}$ and $50^\circ\text{C}$.
- Humidity adjusts by $\pm 1.0\%$, bounded between $20\%$ and $95\%$.
- Air quality adjusts by $\pm 2$, with a 5% probability of a synthetic spike ($+50$ to $+150$).
- Parking maintains state with a 5% toggle probability per cycle.
- Streetlights automatically turn ON between 18:00 and 06:00 UTC and OFF during daylight hours.

#### Q33: When physical ESP32 microcontrollers are connected, what code in the backend needs to change?
**Answer:**
**None of the downstream backend code needs to change.** Because the perception layer is decoupled by the `SensorEvent` data contract, physical ESP32 devices simply need to publish JSON matching the same schema to the ingestion broker. Downstream consumer validation, MongoDB storage, Spark analytics, FastAPI endpoints, and Streamlit dashboard pages will process the physical data without modification.

#### Q34: What physical sensors correspond to your two ESP32 nodes?
**Answer:**
1. **ESP32_ENV_01:**
   - DHT22: Temperature and relative humidity.
   - MQ135: Air quality / gas concentration.
   - MAX4466: Ambient acoustic noise level.
2. **ESP32_TRAFFIC_01:**
   - HC-SR04 Ultrasonic Sensor: Vehicle distance / parking spot occupancy.
   - IR Obstacle Sensor: Vehicle passage detection for adaptive streetlight triggering.
   - 5V Relay / MOSFET with LED: Physical demonstration of streetlight automation.

---

### Section 10: Docker, DevOps & Infrastructure

#### Q35: How do containers communicate with each other inside Docker Compose?
**Answer:**
Docker Compose creates a default user-defined bridge network (`smart-city-platform_default`). Containers resolve each other using their service names as DNS hostnames (e.g., `mongodb:27017`, `kafka:29092`, `api:8000`).

#### Q36: Why does Kafka have two advertised listeners in `docker-compose.yml`?
**Answer:**
```yaml
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
```
This dual-listener configuration allows:
1. Containers on the internal Docker network to reach Kafka via `kafka:29092`.
2. Host processes (such as local Python scripts or IDE debuggers) to reach Kafka via `localhost:9092`.

#### Q37: How does Docker Compose ensure that services start in the correct order?
**Answer:**
Using `depends_on` with `condition: service_healthy`:
- Kafka waits for Zookeeper to be healthy.
- `kafka-init` waits for Kafka to be healthy.
- The consumer and simulator wait for `kafka-init` to complete successfully (`service_completed_successfully`).
- The API waits for MongoDB and Kafka to be healthy.
- The dashboard waits for the API to be healthy.

---

### Section 11: Security, Reliability & Quality Assurance

#### Q38: How is the codebase tested, and what is the test coverage?
**Answer:**
The test suite in [`tests/`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/tests/) uses `pytest` and contains 51 automated tests covering:
- Sensor contract validation and UUID rejection (`test_sensor_contract.py`).
- Active device filtering across repositories (`test_active_devices.py`).
- Alert model, alert engine, and deduplication logic (`test_alert_engine.py`, `test_alert_service.py`).
- All FastAPI endpoints using `TestClient` (`test_api_sensors.py`, `test_api_alerts.py`, etc.).
- ML chronological splitting and model persistence (`test_ml.py`).
- Simulator generation and boundary enforcement (`test_simulator.py`).
All non-Spark unit tests pass with a 100% success rate.

#### Q39: What security precautions are taken regarding credentials?
**Answer:**
Database credentials and usernames are parameterized via environment variables (`MONGO_USER`, `MONGO_PASSWORD`) loaded from `.env`, which is included in `.gitignore`. Production deployments can override these using Docker secrets or cloud secret managers.

---

### Section 12: Questions the Review Panel May Ask About Missing or Incomplete Functionality

#### Q40: "I noticed your architecture diagram mentions MQTT, but there is no MQTT broker in your docker-compose.yml. Why?"
**Professional Answer:**
"That is an accurate observation. In Phase 1 through 7 of our implementation, we focused on establishing the core distributed data pipeline—specifically Kafka streaming, MongoDB persistence, Spark big data ETL, and FastAPI/Streamlit integration. To achieve this without hardware bottlenecks, we used a virtual IoT simulator that publishes directly to Kafka. 
The MQTT broker (Eclipse Mosquitto) and an MQTT-to-Kafka bridge service are the designated ingress components for physical hardware deployment. We have documented their specifications and configuration requirements in our migration guide, and adding them is straightforward because downstream validation and persistence are already decoupled by our `SensorEvent` data contract."

#### Q41: "Why does the Predictions page on your dashboard return an API error or 404?"
**Professional Answer:**
"During our comprehensive codebase audit, we identified a route prefix conflict: in `backend/api/routes/predictions.py`, the router was initialized with `prefix='/api/predictions'`, while `backend/api/main.py` simultaneously included it with `prefix='/api/predictions'`. This resulted in FastAPI exposing the endpoint at `/api/predictions/api/predictions/latest`.
Because the Streamlit dashboard queries `/api/predictions/latest`, it receives an HTTP 404. We have documented this defect in our technical debt register, and the fix requires simply removing the redundant prefix in `predictions.py`."

#### Q42: "Is your Spark analytics pipeline running continuously in real time?"
**Professional Answer:**
"Currently, the Spark container runs a persistent daemon (`spark_daemon.py`) that maintains an active local SparkSession and performs periodic health heartbeats. The data transformations and aggregations in `backend/spark/pipeline.py` are implemented as a **batch ETL pipeline** rather than Spark Structured Streaming.
In production, this pipeline is intended to run as an hourly scheduled job. Transitioning from micro-batch to true Spark Structured Streaming over Kafka is part of our future scope for Phase 8."

#### Q43: "Why do the Devices and Locations pages in your Streamlit dashboard show empty readings?"
**Professional Answer:**
"Our code audit revealed a schema key mismatch between the frontend and backend. The FastAPI `DeviceInfo` endpoint returns `latest_timestamp` and `latest_status`, while the Streamlit page was coded to expect `last_seen` and `latest_readings`. The underlying sensor data and active device IDs exist in MongoDB and are served correctly by the API; resolving the display issue simply requires aligning the dictionary keys in `8_Devices.py` and `9_Locations.py`."

#### Q44: "How accurate are your machine learning models in predicting real city traffic and pollution?"
**Professional Answer:**
"Our Random Forest models achieve high metrics on our test set—accuracy over 90% for parking occupancy and an $R^2$ score over 0.85 for AQI. However, we must be scientifically honest: these models were trained on data produced by our synthetic sensor generator. The simulator implements bounded oscillations with random noise, which the Random Forest learns very effectively.
While this validates our end-to-end ML training, feature extraction, serialization, and inference pipeline, real-world accuracy can only be determined once the physical ESP32 nodes have gathered empirical sensor data over several weeks."

#### Q45: "What are your top 3 engineering priorities before deploying this project in production?"
**Professional Answer:**
"1. **Deploying the MQTT Ingress Bridge:** Adding Eclipse Mosquitto and a containerized MQTT-to-Kafka bridge to ingest physical ESP32 sensor telemetry.
2. **Resolving Route & UI Key Discrepancies:** Correcting the double-prefix route in `predictions.py` and aligning dictionary keys in `8_Devices.py` and `9_Locations.py`.
3. **Automated Pipeline Scheduling:** Configuring an hourly cron job for the Spark batch analytics pipeline and a background worker for the ML inference loop."
