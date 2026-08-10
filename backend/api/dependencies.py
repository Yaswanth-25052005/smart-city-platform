"""FastAPI dependency providers."""

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from backend.config.settings import DATABASE_NAME, MONGO_URI


@lru_cache
def get_mongo_client() -> MongoClient:
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is not configured")
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def get_database() -> Database:
    return get_mongo_client()[DATABASE_NAME]
