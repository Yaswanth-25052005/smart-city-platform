from pymongo import MongoClient
from backend.config.settings import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

sensor_collection = db["sensor_data"]
analytics_collection = db["analytics"]
prediction_collection = db["predictions"]

print("MongoDB Connected")