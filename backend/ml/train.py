import os
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from backend.ml.data_loader import DataLoader
from backend.config.settings import ACTIVE_DEVICES

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def ensure_model_dir():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

def train_parking():
    print("\n--- Training Parking Model ---")
    df = DataLoader.get_raw_data("ESP32_TRAFFIC_01")
    print(f"Total raw records: {len(df)}")
    
    df = DataLoader.extract_features(df, is_training=True)
    print(f"Records after feature extraction & dropna: {len(df)}")
    if len(df) < 20:
        print("Not enough data to train parking model.")
        return

    print(f"Parking occupancy distribution:\n{df['target_parking'].value_counts()}")
    
    train_df, test_df = DataLoader.chronological_split(df)
    
    features = ['hour', 'day_of_week', 'recent_occupancy_mean']
    X_train, y_train = train_df[features], train_df['target_parking']
    X_test, y_test = test_df[features], test_df['target_parking']
    
    model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    print("\nEvaluation Metrics:")
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0))
    }
    for k, v in metrics.items():
        print(f"{k.capitalize()}: {v:.4f}")
    
    ensure_model_dir()
    model_path = os.path.join(MODEL_DIR, "parking_model.joblib")
    joblib.dump({"model": model, "metrics": metrics, "version": "RandomForestClassifier_v1"}, model_path)
    print(f"Saved parking model to {model_path}")


def train_air_quality():
    print("\n--- Training Air Quality Model ---")
    df = DataLoader.get_raw_data("ESP32_ENV_01")
    print(f"Total raw records: {len(df)}")
    
    df = DataLoader.extract_features(df, is_training=True)
    print(f"Records after feature extraction & dropna: {len(df)}")
    if len(df) < 20:
        print("Not enough data to train AQI model.")
        return
        
    print(f"AQI stats - Min: {df['target_aqi'].min():.2f}, Max: {df['target_aqi'].max():.2f}, Mean: {df['target_aqi'].mean():.2f}")

    train_df, test_df = DataLoader.chronological_split(df)
    
    features = ['hour', 'temperature', 'humidity', 'recent_aqi_mean']
    X_train, y_train = train_df[features], train_df['target_aqi']
    X_test, y_test = test_df[features], test_df['target_aqi']
    
    model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    print("\nEvaluation Metrics:")
    metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "rmse": float(mean_squared_error(y_test, y_pred) ** 0.5),
        "r2_score": float(r2_score(y_test, y_pred))
    }
    for k, v in metrics.items():
        print(f"{k.upper()}: {v:.4f}")
    
    ensure_model_dir()
    model_path = os.path.join(MODEL_DIR, "air_quality_model.joblib")
    joblib.dump({"model": model, "metrics": metrics, "version": "RandomForestRegressor_v1"}, model_path)
    print(f"Saved AQI model to {model_path}")

if __name__ == "__main__":
    print("Starting ML Training Pipeline...")
    
    if "ESP32_TRAFFIC_01" in ACTIVE_DEVICES:
        train_parking()
        
    if "ESP32_ENV_01" in ACTIVE_DEVICES:
        train_air_quality()
        
    print("\nTraining completed.")
