from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from app.services.redis_client import redis_client

from app.routes import base_router
from app.routes import places_router

app = FastAPI()

app.include_router(base_router.router)
app.include_router(places_router.router)

origins = [
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Place Wrapper is Running!"}

@app.post("/cache/{key}")
async def set_cache(key: str, value: str = Body(..., embed=True)):
    await redis_client.set(key, value)
    return {"message": f"Stored {key} -> {value}"}

@app.get("/cache/{key}")
async def get_cache(key: str):
    value = await redis_client.get(key)
    if value:
        return {"key": key, "value": value}
    return {"message": "Key not found"}