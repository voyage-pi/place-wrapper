import httpx
import json

from app.models.get_photos.request_models import Photo_gRPC
from app.models.get_photos.response_models import Photo
from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client

BASE_GOOGLE_URL = "https://places.googleapis.com/v1/"

async def get_photo(request: Photo_gRPC):
    """
    Fetch a photo using the GET method with the provided photo reference.
    """

    photo_reference = request.gRPC
    max_width = request.maxWidthPx
    max_height = request.maxHeightPx

    cache_key = f"photo:{photo_reference}"

    cached_photo = await redis_client.get(cache_key)
    if cached_photo:
        print("FROM CACHE")
        return Photo(**json.loads(cached_photo))
    
    photo_url = f"{BASE_GOOGLE_URL}{photo_reference}/media?maxWidthPx={max_width}&maxHeightPx={max_height}"

    headers = {
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(photo_url, headers=headers)
        data = response.json()

    print("GOOGLE API RESPONSE:", json.dumps(data, indent=2))

    if "photoUri" in data:
        photo_uri = data["photoUri"]
    else:
        return {"error": "Photo URI not found in the response"}
    
    photo_data = {"name": data.get("name", "Unnamed Photo"), "uri": photo_uri}
    await redis_client.set(cache_key, json.dumps(photo_data), expire=3600)

    return Photo(name=photo_data["name"], uri=photo_data["uri"])
