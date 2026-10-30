import os
import joblib
import uuid
from datetime import datetime, timezone, timedelta
from backend.ml.data_loader import DataLoader
from backend.domain.prediction import PredictionModel
from backend.database.prediction_repository import PredictionRepository
from backend.config.settings import ACTIVE_DEVICES

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def load_model(name: str):
    path = os.path.join(MODEL_DIR, name)
    if os.path.exists(path):
        return joblib.load(path)
    return None

def predict_parking():
    data = load_model("parking_model.joblib")
    if not data:
        print("Parking model not found. Run training first.")
        return
        
    model = data.get("model")
    metrics = data.get("metrics")
    version = data.get("version", "RandomForest_v1")
    
    df = DataLoader.get_raw_data("ESP32_TRAFFIC_01")
    if df.empty:
        return
        
    df_feat = DataLoader.extract_features(df, is_training=False)
    if df_feat.empty:
        return
        
    latest = df_feat.iloc[-1:]
    features = ['hour', 'day_of_week', 'recent_occupancy_mean']
    X = latest[features]
    
    # Predict probabilities for parking (occupancy state/probability)
    # class 1 is True/Occupied
    prob = model.predict_proba(X)[0]
    
    # If the model didn't learn both classes, predict_proba might only have 1 column. Handle this gracefully:
    if len(prob) == 2:
        occupancy_prob = prob[1]
    else:
        # Check classes_
        if model.classes_[0] == 1.0:
            occupancy_prob = prob[0]
        else:
            occupancy_prob = 0.0
            
    target_timestamp = datetime.now(timezone.utc) + timedelta(seconds=60)
    
    pred = PredictionModel(
        prediction_id=str(uuid.uuid4()),
        prediction_type="parking",
        device_id="ESP32_TRAFFIC_01",
        location_id=latest['location_id'].iloc[0],
        target_timestamp=target_timestamp,
        predicted_value=occupancy_prob,
        model_version=version,
        evaluation_metrics=metrics,
        created_at=datetime.now(timezone.utc)
    )
    
    PredictionRepository.insert(pred)
    print(f"Generated parking prediction: {occupancy_prob:.2f} prob of occupancy")

def predict_aqi():
    data = load_model("air_quality_model.joblib")
    if not data:
        print("AQI model not found. Run training first.")
        return
        
    model = data.get("model")
    metrics = data.get("metrics")
    version = data.get("version", "RandomForestRegressor_v1")
        
    df = DataLoader.get_raw_data("ESP32_ENV_01")
    if df.empty:
        return
        
    df_feat = DataLoader.extract_features(df, is_training=False)
    if df_feat.empty:
        return
        
    latest = df_feat.iloc[-1:]
    features = ['hour', 'temperature', 'humidity', 'recent_aqi_mean']
    X = latest[features]
    
    pred_val = model.predict(X)[0]
    target_timestamp = datetime.now(timezone.utc) + timedelta(seconds=60)
    
    pred = PredictionModel(
        prediction_id=str(uuid.uuid4()),
        prediction_type="air_quality",
        device_id="ESP32_ENV_01",
        location_id=latest['location_id'].iloc[0],
        target_timestamp=target_timestamp,
        predicted_value=pred_val,
        model_version=version,
        evaluation_metrics=metrics,
        created_at=datetime.now(timezone.utc)
    )
    
    PredictionRepository.insert(pred)
    print(f"Generated AQI prediction: {pred_val:.2f}")

if __name__ == "__main__":
    print("Running predictions...")
    if "ESP32_TRAFFIC_01" in ACTIVE_DEVICES:
        predict_parking()
    if "ESP32_ENV_01" in ACTIVE_DEVICES:
        predict_aqi()
    print("Done.")
