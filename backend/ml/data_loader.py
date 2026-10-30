import pandas as pd
from datetime import datetime, timezone
from typing import Tuple, Dict, Any
from backend.database.connection import sensor_collection
from backend.config.settings import ACTIVE_DEVICES

class DataLoader:
    @staticmethod
    def get_raw_data(device_id: str) -> pd.DataFrame:
        """Fetches all data for a specific device and returns a DataFrame sorted by timestamp."""
        cursor = sensor_collection.find({"device_id": device_id}, {"_id": 0})
        df = pd.DataFrame(list(cursor))
        if df.empty:
            return df
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df

    @staticmethod
    def extract_features(df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Extracts features. If is_training is False, it processes just the latest row.
        """
        if df.empty:
            return df
            
        df = df.copy()
        
        # Time features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Determine device type based on device_id
        device_id = df['device_id'].iloc[0]
        if device_id == "ESP32_TRAFFIC_01":
            # Parking features
            df['parking_occupied_num'] = df['parking_occupied'].astype(float)
            # Rolling occupancy over last 5 events (~15 seconds)
            df['recent_occupancy_mean'] = df['parking_occupied_num'].rolling(window=5, min_periods=1).mean()
            
            # The target for training is the occupancy at T+60s (roughly 20 events later)
            # But wait, the user asked to predict "parking occupancy state/probability".
            # For parking, we can predict the state in 1 minute (20 steps).
            if is_training:
                df['target_parking'] = df['parking_occupied_num'].shift(-20)
                
            # Drop rows with NaN targets (the end of the dataset) or NaN features
            if is_training:
                df = df.dropna(subset=['target_parking', 'recent_occupancy_mean'])
            else:
                df = df.dropna(subset=['recent_occupancy_mean'])
                
        elif device_id == "ESP32_ENV_01":
            # Environment features
            df['recent_aqi_mean'] = df['air_quality'].rolling(window=5, min_periods=1).mean()
            
            # Forward fill missing temperature/humidity to avoid dropping useful AQI rows
            df['temperature'] = df['temperature'].ffill().bfill()
            df['humidity'] = df['humidity'].ffill().bfill()
            
            # Target is air quality at T+60s (roughly 20 events later)
            if is_training:
                df['target_aqi'] = df['air_quality'].shift(-20)
                df = df.dropna(subset=['target_aqi', 'recent_aqi_mean', 'temperature', 'humidity'])
            else:
                df = df.dropna(subset=['recent_aqi_mean', 'temperature', 'humidity'])
                
        return df

    @staticmethod
    def chronological_split(df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Splits the dataframe strictly by time to prevent data leakage."""
        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        return train_df, test_df
