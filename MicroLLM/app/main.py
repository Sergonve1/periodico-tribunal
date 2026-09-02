from fastapi import FastAPI
from app.kafka.consumer import start_kafka, stop_kafka
from app.services.mongo import init_mongo, close_mongo

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_mongo()
    await start_kafka()

@app.on_event("shutdown")
async def shutdown_event():
    await stop_kafka()
    close_mongo()

@app.get("/health")
async def health_check():
    return {"status": "OK"}
