from motor.motor_asyncio import AsyncIOMotorClient

_mongo_client = None
_mongo_collection = None

def init_mongo():
    global _mongo_client, _mongo_collection
    _mongo_client = AsyncIOMotorClient("mongodb://mongodb:27017/Newspaper")
    _mongo_collection = _mongo_client["Newspaper"]["embeddings"]
    print("✅ Conectado a MongoDB")

def get_mongo_collection():
    return _mongo_collection

def close_mongo():
    if _mongo_client:
        _mongo_client.close()
        print("🛑 MongoDB cerrado.")
