from backend.database.connection import sensor_collection


class SensorRepository:

    @staticmethod
    def insert(data):
        return sensor_collection.insert_one(data)

    @staticmethod
    def find_latest(limit=10):
        return list(
            sensor_collection.find().sort("_id", -1).limit(limit)
        )

    @staticmethod
    def find_all():
        return list(sensor_collection.find())

    @staticmethod
    def find_by_device(device_id):
        return list(
            sensor_collection.find({"device_id": device_id})
        )

    @staticmethod
    def delete_all():
        sensor_collection.delete_many({})