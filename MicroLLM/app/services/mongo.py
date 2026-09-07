import os

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27018/Newspaper")

_mongo_client = None
_mongo_collection = None

def init_mongo():
    global _mongo_client, _mongo_collection
    _mongo_client = AsyncIOMotorClient(MONGO_URI)
    _mongo_collection = _mongo_client["Newspaper"]["embeddings"]
    print(f"✅ Conectado a MongoDB ({MONGO_URI})")

def get_mongo_collection():
    return _mongo_collection

def close_mongo():
    if _mongo_client:
        _mongo_client.close()
        print("🛑 MongoDB cerrado.")
