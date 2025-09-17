import os
from functools import lru_cache
from typing import Optional, Tuple
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def _resolve_mongo_uri() -> Tuple[str, str]:
    """Resolve MongoDB URI based on environment.

    APP_ENV: 'development'|'production' (defaults to 'production' if not set)
    - development: build URI from MONGODB_HOST and MONGODB_PORT (defaults localhost:27017)
    - production: use MONGODB_CONNECTION_STRING (required)
    Returns: (uri, mode)
    """
    env = (os.getenv("APP_ENV") or os.getenv("ENV") or "production").strip().lower()
    if env in ("development", "dev", "local"):
        host = os.getenv("MONGODB_HOST", "localhost")
        port = os.getenv("MONGODB_PORT", "27017")
        uri = f"mongodb://{host}:{port}/"
        print(f"[mongo] Using development MongoDB at {uri}")
        return uri, "development"
    # production/default
    uri = os.getenv("MONGODB_CONNECTION_STRING")
    if not uri:
        raise RuntimeError("MONGODB_CONNECTION_STRING not set in environment for production mode")
    print("[mongo] Using production MongoDB via connection string")
    return uri, "production"


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    uri, _mode = _resolve_mongo_uri()
    return MongoClient(uri, serverSelectionTimeoutMS=8000)

@lru_cache(maxsize=1)
def get_database():
    db_name = os.getenv("MONGODB_DATABASE_NAME", "skillmateAiDb")
    client = get_mongo_client()
    return client[db_name]
