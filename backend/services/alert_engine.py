import logging
from typing import List, Dict, Any
from backend.database.connection import sensor_collection, analytics_collection
from backend.services.alert_service import AlertService
from backend.domain.alert import AlertType, AlertSeverity
from backend.config import alert_rules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertEngine")

class AlertEngine:
    @staticmethod
    def run():
        logger.info("Starting Alert Engine Batch Job")
        AlertService.setup()

        # 1. Evaluate device-level alerts from sensor_data
        logger.info("Evaluating real-time sensor data rules...")
        # Fetch latest records (e.g., last 200 for processing)
        recent_sensors = list(sensor_collection.find().sort("timestamp", -1).limit(200))
        
        # We group by device to only evaluate the LATEST state of each device
        latest_by_device = {}
        for s in recent_sensors:
            dev_id = s.get("device_id")
            if dev_id and dev_id not in latest_by_device:
                latest_by_device[dev_id] = s

        for dev_id, s in latest_by_device.items():
            loc_id = s.get("location_id", "UNKNOWN")
            
            # High Temperature
            temp = s.get("temperature")
            if temp is not None:
                is_abnormal = temp > alert_rules.THRESHOLD_HIGH_TEMPERATURE
                AlertService.evaluate_condition(
                    alert_type=AlertType.HIGH_TEMPERATURE,
                    severity=AlertSeverity.HIGH if temp > alert_rules.THRESHOLD_HIGH_TEMPERATURE + 5 else AlertSeverity.MEDIUM,
                    location_id=loc_id,
                    metric="temperature",
                    value=temp,
                    threshold=alert_rules.THRESHOLD_HIGH_TEMPERATURE,
                    message=f"High temperature detected: {temp}°C",
                    is_abnormal=is_abnormal,
                    device_id=dev_id
                )
                
                # Data Quality (Temperature out of extreme bounds)
                is_invalid = temp < alert_rules.THRESHOLD_TEMP_MIN or temp > alert_rules.THRESHOLD_TEMP_MAX
                AlertService.evaluate_condition(
                    alert_type=AlertType.DATA_QUALITY,
                    severity=AlertSeverity.LOW,
                    location_id=loc_id,
                    metric="temperature",
                    value=temp,
                    threshold=alert_rules.THRESHOLD_TEMP_MIN,
                    message=f"Implausible temperature value: {temp}°C",
                    is_abnormal=is_invalid,
                    device_id=dev_id
                )

            # High Noise
            noise = s.get("noise")
            if noise is not None:
                is_abnormal = noise > alert_rules.THRESHOLD_HIGH_NOISE
                AlertService.evaluate_condition(
                    alert_type=AlertType.HIGH_NOISE,
                    severity=AlertSeverity.MEDIUM,
                    location_id=loc_id,
                    metric="noise",
                    value=noise,
                    threshold=alert_rules.THRESHOLD_HIGH_NOISE,
                    message=f"High noise detected: {noise}dB",
                    is_abnormal=is_abnormal,
                    device_id=dev_id
                )
                
            # Streetlight Anomaly
            # For demo: if streetlight_on is False but it's reported
            sl = s.get("streetlight_on")
            if sl is not None:
                # We'll mock the condition: if it's off when it shouldn't be (e.g. simulated anomaly)
                # We can't know time of day reliably here without complexity, let's just use it being off as an anomaly for demo if the simulator randomly sets it to False for anomaly
                is_abnormal = (sl == False)
                AlertService.evaluate_condition(
                    alert_type=AlertType.STREETLIGHT_ANOMALY,
                    severity=AlertSeverity.LOW,
                    location_id=loc_id,
                    metric="streetlight_on",
                    value=0.0,
                    threshold=1.0,
                    message="Streetlight is OFF when it should be ON",
                    is_abnormal=is_abnormal,
                    device_id=dev_id
                )


        # 2. Evaluate location-level alerts from analytics
        logger.info("Evaluating aggregated analytics rules...")
        recent_analytics = list(analytics_collection.find().sort("processed_at", -1).limit(50))
        
        # Group by location and metric to get latest aggregated state
        latest_analytics = {}
        for a in recent_analytics:
            key = (a.get("location_id"), a.get("metric"))
            if key not in latest_analytics:
                latest_analytics[key] = a

        for (loc_id, metric), a in latest_analytics.items():
            avg_val = a.get("average")
            if avg_val is None:
                continue

            if metric == "parking":
                # Convert average (which is percentage occupancy 0-1) to percentage for threshold comparison
                # Note: The simulator aggregations might have average as 0-1 or 0-100.
                # Let's assume it's 0-1 if it's based on parking_occupied boolean. Wait, mean of bool is 0-1.
                # Threshold is 90.0, so we multiply avg_val by 100.
                occupancy_pct = avg_val * 100.0
                is_abnormal = occupancy_pct > alert_rules.THRESHOLD_PARKING_CONGESTION
                AlertService.evaluate_condition(
                    alert_type=AlertType.PARKING_CONGESTION,
                    severity=AlertSeverity.HIGH,
                    location_id=loc_id,
                    metric="parking",
                    value=occupancy_pct,
                    threshold=alert_rules.THRESHOLD_PARKING_CONGESTION,
                    message=f"Parking congestion detected: {occupancy_pct:.1f}%",
                    is_abnormal=is_abnormal,
                    device_id=None
                )
            
            elif metric == "air_quality":
                is_abnormal = avg_val > alert_rules.THRESHOLD_AIR_QUALITY
                AlertService.evaluate_condition(
                    alert_type=AlertType.AIR_QUALITY,
                    severity=AlertSeverity.CRITICAL if avg_val > alert_rules.THRESHOLD_AIR_QUALITY + 50 else AlertSeverity.HIGH,
                    location_id=loc_id,
                    metric="air_quality",
                    value=avg_val,
                    threshold=alert_rules.THRESHOLD_AIR_QUALITY,
                    message=f"Poor air quality detected: {avg_val:.1f} AQI",
                    is_abnormal=is_abnormal,
                    device_id=None
                )

        logger.info("Alert Engine Batch Job Completed")

if __name__ == "__main__":
    AlertEngine.run()
