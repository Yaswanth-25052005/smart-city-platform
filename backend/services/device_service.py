from backend.database.dashboard_repository import DashboardRepository
from backend.database.repository import SensorRepository
from backend.database.connection import sensor_collection
from backend.domain.device import DeviceInfo, LocationInfo
from backend.domain.sensor import SensorEvent
from typing import List, Optional

class DeviceService:
    @staticmethod
    def get_devices() -> List[str]:
        return DashboardRepository.get_device_ids()
        
    @staticmethod
    def get_device(device_id: str) -> Optional[DeviceInfo]:
        docs = SensorRepository.find({"device_id": device_id}, limit=1)
        if not docs:
            return None
        
        latest = docs[0]
        from backend.services.sensor_service import SensorService
        mapped_status = SensorService.map_sensor_doc(latest.copy())
        
        return DeviceInfo(
            device_id=device_id,
            location_id=latest.get("location_id", "UNKNOWN"),
            latest_timestamp=latest.get("timestamp"),
            latest_status=mapped_status
        )

    @staticmethod
    def get_locations() -> List[str]:
        return DashboardRepository.get_location_ids()
        
    @staticmethod
    def get_location(location_id: str) -> Optional[LocationInfo]:
        docs = SensorRepository.find({"location_id": location_id}, limit=1)
        if not docs:
            return None
            
        latest = docs[0]
        # In a real app we might aggregate, but for now we get distinct devices in this location
        # by searching the collection. Since this can be slow, we'll keep it simple or use distinct.
        # However, we only have DashboardRepository.get_device_ids() which is global.
        # We can query it by looking at sensor_collection directly, but let's just do a distinct directly here 
        # or mock it up. Actually, we'll query sensor_collection for distinct devices in location.
        
        devices_in_loc = sensor_collection.distinct("device_id", {"location_id": location_id})
        
        return LocationInfo(
            location_id=location_id,
            device_count=len(devices_in_loc),
            devices=devices_in_loc,
            latest_timestamp=latest.get("timestamp")
        )
