import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone
from backend.ml.data_loader import DataLoader
from backend.domain.prediction import PredictionModel

def test_chronological_split():
    # Create sample chronological dataframe
    now = datetime.now(timezone.utc)
    data = []
    for i in range(100):
        data.append({"timestamp": now + timedelta(seconds=i), "val": i})
    
    df = pd.DataFrame(data)
    train_df, test_df = DataLoader.chronological_split(df, test_size=0.2)
    
    assert len(train_df) == 80
    assert len(test_df) == 20
    
    # Verify no overlap and strict time ordering
    assert train_df.iloc[-1]["timestamp"] < test_df.iloc[0]["timestamp"]
    
def test_prediction_model_schema():
    # Verify the pydantic schema accepts valid metrics dict
    pred = PredictionModel(
        prediction_id="123",
        prediction_type="parking",
        device_id="ESP32_TRAFFIC_01",
        location_id="ZONE_B",
        target_timestamp=datetime.now(timezone.utc),
        predicted_value=0.85,
        model_version="v1",
        evaluation_metrics={"accuracy": 0.9},
        created_at=datetime.now(timezone.utc)
    )
    
    assert pred.predicted_value == 0.85
    assert pred.evaluation_metrics["accuracy"] == 0.9
