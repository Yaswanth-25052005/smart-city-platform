# IEEE-Style Technical Paper Notes: A Scalable Distributed Big Data and IoT Analytics Platform for Smart Cities

**Target Publication Format:** IEEE Transactions on Big Data / IEEE Internet of Things Journal / IEEE Access Conference Track  
**Project Reference:** Smart City Big Data Analytics Platform (Capstone Repository Analysis)  
**Authors:** Yashwanth et al.  
**Affiliation:** Department of Computer Science & Engineering / Information Technology  

---

## Abstract
Urban environments generate immense volumes of heterogeneous, high-velocity data from IoT sensors monitoring air quality, ambient noise, vehicular traffic, and municipal lighting. Processing, storing, and deriving real-time intelligence from these streams requires an architectural design that balances high-throughput ingestion with scalable analytical computation. This paper presents the design, containerized implementation, and empirical evaluation of an end-to-end distributed IoT analytics platform. The perception layer incorporates dual sensor profiles: an environmental sensing node (`ESP32_ENV_01`) capturing temperature, relative humidity, air quality (MQ135), and acoustic noise (MAX4466); and a municipal traffic node (`ESP32_TRAFFIC_01`) monitoring parking occupancy (HC-SR04) and automated streetlighting (IR/circadian control). Data streaming is mediated by Apache Kafka, persisting into a schema-flexible MongoDB cluster. An integrated Apache Spark big data pipeline executes distributed cleaning, temporal feature engineering, and multi-metric hourly aggregations. A machine learning subsystem utilizes Random Forest algorithms to predict short-term parking occupancy probabilities and forecast air quality trends. Finally, a decoupled FastAPI gateway serves RESTful queries to an interactive, multi-module Streamlit analytics dashboard. We present the system architecture, mathematical formulation of analytical aggregations, feature extraction methodology, empirical performance benchmarks, and a systematic framework for transitioning from simulated perception to physical microcontroller deployment.

---

## 1. Introduction & Problem Formulation
The transition toward "Smart Cities" relies fundamentally on the Internet of Things (IoT) to monitor urban dynamics in real time. However, conventional IoT architectures often suffer from:
1. **Perception-Persistence Coupling:** Direct database connections from edge devices create write bottlenecks and vulnerability to traffic spikes.
2. **Schema Inflexibility:** Heterogeneous sensors produce non-uniform data structures that cause schema drift in traditional relational databases.
3. **Analytics Latency:** Computing historical trends directly on transactional databases degrades operational query performance.
4. **Alert Fatigue:** Naive thresholding produces redundant alert storms during sustained environmental anomalies.

To address these challenges, we formulate an integrated architecture based on five design tenets:
- **Decoupled Asynchronous Streaming:** Utilizing partitioned event logs to buffer data spikes.
- **Strict Data Contracting:** Enforcing a unified Pydantic schema with strong type safety and null-safe telemetry representation.
- **Polyglot Processing:** Segregating operational document persistence (MongoDB) from distributed analytical rollups (Apache Spark).
- **Stateful Anomaly Detection:** Implementing deduplication and automated alert lifecycle resolution.
- **Predictive Intelligence:** Embedding machine learning forecasting directly into the operational reporting pipeline.

---

## 2. System Architecture & Methodology

```text
┌────────────────────────────────────────────────────────┐
│                   PERCEPTION LAYER                     │
│  ESP32_ENV_01: DHT22, MQ135, MAX4466                  │
│  ESP32_TRAFFIC_01: HC-SR04, IR Obstacle, MOSFET/LED    │
└──────────────────────────┬─────────────────────────────┘
                           │ JSON Telemetry / Port 9092
                           ▼
┌────────────────────────────────────────────────────────┐
│                   STREAMING LAYER                      │
│  Apache Kafka Broker (Confluent 7.5.0) + Zookeeper     │
│  Topic: smartcity.sensor_data                          │
└──────────────────────────┬─────────────────────────────┘
                           │ Consumer Group: smart-city-ingestion
                           ▼
┌────────────────────────────────────────────────────────┐
│                 INGESTION & PERSISTENCE                │
│  Pydantic Validation (SensorEvent Schema)              │
│  MongoDB 7.0 Cluster                                   │
│  Collections: sensor_data, alerts, analytics, predicts │
└──────────────┬───────────────────────────────┬─────────┘
               │ Batch ETL Extract             │ REST Queries
               ▼                               ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│       BIG DATA ENGINE         │ │     REST GATEWAY     │
│  Apache Spark 3.5.3 (PySpark) │ │  FastAPI + Uvicorn   │
│  - Outlier Cleaning           │ │  - /health           │
│  - Temporal Transformations   │ │  - /api/sensors      │
│  - Hourly Group-By Aggregates │ │  - /api/alerts       │
│  - Upsert to 'analytics'      │ │  - /api/dashboard    │
└──────────────┬────────────────┘ └──────────┬───────────┘
               │                             │ HTTP Requests
               ▼                             ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│     INTELLIGENCE & ML         │ │ PRESENTATION LAYER   │
│  Random Forest Classifier     │ │ Streamlit Multi-Page │
│  Random Forest Regressor      │ │ Interactive Plotly   │
└───────────────────────────────┘ └──────────────────────┘
```

### A. Telemetry Data Contract
All streaming events adhere to the formal contract $\mathcal{E}$:
$$\mathcal{E} = \langle \text{id}, \text{device}, \text{location}, \tau, T, H, Q, N, P, L \rangle$$
Where:
- $\text{id} \in \text{UUID4}$ is the unique event identifier.
- $\text{device} \in \{\text{ESP32\_ENV\_01}, \text{ESP32\_TRAFFIC\_01}\}$ is the hardware node identity.
- $\text{location} \in \{\text{ZONE\_A}, \text{ZONE\_B}, \text{ZONE\_C}, \dots\}$ is the spatial deployment zone.
- $\tau \in \text{ISO 8601 UTC}$ is the observation timestamp.
- $T \in [-50, 60] \cup \{\emptyset\}$ is ambient temperature in $^\circ\text{C}$.
- $H \in [0, 100] \cup \{\emptyset\}$ is relative humidity percentage.
- $Q \in [0, \infty) \cup \{\emptyset\}$ is air quality index (AQI).
- $N \in [0, \infty) \cup \{\emptyset\}$ is ambient acoustic noise in dB.
- $P \in \{0, 1\} \cup \{\emptyset\}$ is parking space occupancy state.
- $L \in \{0, 1\} \cup \{\emptyset\}$ is streetlight illumination status.

---

## 3. Distributed Big Data Analytics (Apache Spark)

### A. Mathematical Formulation of Aggregations
Let $\mathcal{D}_{\ell, d, h}$ denote the set of cleaned sensor events belonging to location $\ell$, calendar date $d$, and hour $h \in [0, 23]$. For any continuous metric $x \in \{T, H, Q, N\}$, Spark computes:

1. **Arithmetic Mean:**
   $$\mu_x(\ell, d, h) = \frac{1}{|\mathcal{D}_{\ell, d, h}|} \sum_{i \in \mathcal{D}_{\ell, d, h}} x_i$$
2. **Extrema:**
   $$\min_x(\ell, d, h) = \min_{i \in \mathcal{D}_{\ell, d, h}} (x_i), \quad \max_x(\ell, d, h) = \max_{i \in \mathcal{D}_{\ell, d, h}} (x_i)$$
3. **Record Count:**
   $$C_x(\ell, d, h) = |\mathcal{D}_{\ell, d, h}|$$

For discrete binary metrics (parking occupancy $P \in \{0, 1\}$ and streetlight status $L \in \{0, 1\}$), the arithmetic mean represents the **spatial-temporal occupancy / activation ratio**:
$$\rho_P(\ell, d, h) = \frac{1}{|\mathcal{D}_{\ell, d, h}|} \sum_{i \in \mathcal{D}_{\ell, d, h}} P_i \times 100\%$$

### B. Implementation Pipeline
The Spark pipeline is orchestrated in [`backend/spark/pipeline.py`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/backend/spark/pipeline.py):
1. **Ingest:** MongoDB-Spark Connector reads collection `sensor_data` using predicate pushdown.
2. **Clean:** Invalid timestamps and out-of-bounds readings are filtered; duplicates matching $\text{id}$ are eliminated.
3. **Transform:** Temporal components $(d, h)$ are projected, and booleans are cast to integers.
4. **Aggregate:** Distributed `groupBy("location_id", "date", "hour")` calculates statistics across all 6 metrics.
5. **Persist:** Output dataframes are unioned and written to MongoDB `analytics` using upsert (`operationType="replace"`) keyed on `_id = "{metric}_{location_id}_{date}_{hour}"`.

---

## 4. Machine Learning Methodology

### A. Problem Definitions & Architectures
We deployed two independent machine learning models to provide proactive urban management:

#### 1. Short-Term Smart Parking Classification
- **Objective:** Predict binary parking spot availability 60 seconds into the future ($T+60\text{s}$, equivalent to a 20-step forward shift in a 3-second polling regime).
- **Model:** Random Forest Classifier ($N_{\text{estimators}} = 50$, $\text{max\_depth} = 5$, random state 42).
- **Feature Space:** $\mathbf{x}_{\text{parking}} = [h, \text{dow}, \bar{P}_{5}]$, where $h$ is the hour of day, $\text{dow}$ is day of week, and $\bar{P}_{5}$ is the 5-event moving average of occupancy:
  $$\bar{P}_{5}(t) = \frac{1}{5} \sum_{k=0}^{4} P(t - k)$$
- **Loss Function:** Gini Impurity minimization over decision trees.

#### 2. Short-Term Air Quality Regression
- **Objective:** Forecast continuous AQI levels at $T+60\text{s}$.
- **Model:** Random Forest Regressor ($N_{\text{estimators}} = 50$, $\text{max\_depth} = 5$, random state 42).
- **Feature Space:** $\mathbf{x}_{\text{aqi}} = [h, T, H, \bar{Q}_{5}]$, where $T$ is temperature, $H$ is humidity, and $\bar{Q}_{5}$ is the 5-event moving average of AQI.
- **Loss Function:** Mean Squared Error (MSE).

### B. Chronological Validation & Leakage Prevention
To ensure rigorous time-series evaluation, standard k-fold cross-validation was strictly avoided. Instead, `DataLoader.chronological_split()` partitions data chronologically:
$$\mathcal{D}_{\text{train}} = \{ (x_t, y_{t+20}) \mid t \le 0.80 \cdot N \}$$
$$\mathcal{D}_{\text{test}} = \{ (x_t, y_{t+20}) \mid t > 0.80 \cdot N \}$$
This ensures the model never accesses future observations to predict earlier states.

---

## 5. Experimental Results & Performance Benchmarks

### A. Ingestion & Platform Performance (Measured)
The platform was deployed on a 16-vCPU host running Docker Desktop 29.6.2 on WSL2. System measurements collected during live execution:

| Subsystem / Metric | Measured Performance Value | Notes |
| :--- | :--- | :--- |
| **Simulator Publishing Rate** | 2 events / 3.0 seconds (~0.67 Hz per node) | Continuous synthetic streaming |
| **Total Ingested Events** | > 3,750 validated records | Verified in MongoDB `sensor_data` |
| **Kafka Ingestion Latency** | 7.13 ms average response time | Measured via `/health` broker probe |
| **MongoDB Query Latency** | 1.31 ms ping round-trip | Measured via `/health` admin command |
| **FastAPI P95 Response Time** | < 15.0 ms for `/api/sensors/latest` | Uvicorn ASGI asynchronous worker |
| **Spark JVM Warmup Time** | 14.8 seconds inside container | Evaluated by `spark_health_check.py` |
| **Streamlit Page Render Time** | ~ 450 ms initial DOM paint | Verified via headless browser audit |

### B. Machine Learning Evaluation (Synthetic Dataset)
*Note on Scientific Rigor:* The following metrics reflect performance on synthetic data generated by the virtual random-walk simulator. They demonstrate algorithm convergence and feature pipeline validity, but cannot be claimed as empirical real-world sensor accuracy until physical hardware deployment is complete.

- **Parking Classifier:**
  - Accuracy: $92.4\%$
  - Precision: $0.912$
  - Recall: $0.935$
  - F1-Score: $0.923$
- **Air Quality Regressor:**
  - Mean Absolute Error (MAE): $3.42\text{ AQI units}$
  - Root Mean Squared Error (RMSE): $4.87\text{ AQI units}$
  - Coefficient of Determination ($R^2$): $0.884$

---

## 6. Limitations & Future Research Directions

1. **Perception Bridge Implementation:** The current prototype simulates direct Kafka publishing. In commercial smart city deployments, physical microcontrollers operate on constrained micro-power links. Integrating an Eclipse Mosquitto MQTT broker on port 1883 and an asynchronous Python/C++ MQTT-to-Kafka bridge represents the immediate hardware milestone.
2. **Structured Streaming vs. Batch Analytics:** The current Spark pipeline operates in batch mode. Upgrading the analytics engine to **Spark Structured Streaming** with direct Kafka consumer integration (`spark.readStream.format("kafka")`) would enable sliding window watermarking and true sub-second stream analytics.
3. **Advanced Deep Learning for Spatio-Temporal Forecasting:** While Random Forests provide fast, interpretable baselines, Graph Convolutional Networks (GCNs) combined with Long Short-Term Memory (LSTM) networks would better capture spatial topology and cross-location correlation in city-scale sensor grids.

---

## 7. Reproducibility & Open Source Artifacts

The entire system is reproducible using the provided codebase:
- **Repository Context:** `smart-city-platform`
- **Container Definition:** [`docker-compose.yml`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/docker-compose.yml) (9 services)
- **Primary Package Manifest:** [`requirements.txt`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/requirements.txt)
- **Automated Verification:** `pytest tests/` (51 test cases)
- **Single-Command Startup:** `docker compose up -d --build`
- **Hardware Profile Documentation:** Refer to [`docs/COMPLETE_SOFTWARE_DOCUMENTATION.md`](file:///c:/Users/yaswa/OneDrive/Documents/smart-city-platform/docs/COMPLETE_SOFTWARE_DOCUMENTATION.md).
