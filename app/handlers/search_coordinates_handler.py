import httpx
import json

from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client
from app.models.search_coordinates.request_models import PlaceName
from app.models.search_coordinates.response_models import Location

BASE_GOOGLE_URL = "https://maps.googleapis.com/maps/api/geocode/json?"


async def search_coordinates(request: PlaceName):
    """
    Fetch coordinates from Google Places API.
    Normalizes the response before returning.
    """

    # Extract parameters from request
    place_name = request.place_name

    # Generate a Redis cache key
    cache_key = f"coordinates:{place_name}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print("FROM CACHE")
        return json.loads(cached_data)

    # Prepare API request headers (no need for extra headers)
    headers = {
        "Content-Type": "application/json",
    }

    # Prepare request payload
    payload = {"address": place_name, "key": GOOGLE_MAPS_API_KEY}

    # Make the API request
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_GOOGLE_URL, headers=headers, params=payload)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

    print("GOOGLE API RAW RESPONSE:", json.dumps(data, indent=2))

    # Normalize the response
    if data.get("results"):
        location = data["results"][0]["geometry"]["location"]
        place_id = data["results"][0]["place_id"]
        # Directly return the Location model with latitude and longitude
        coordinates = Location(
            latitude=location["lat"], longitude=location["lng"], place_id=place_id
        )
        # Store the response in Redis cache (store as dict, not JSON string)
        await redis_client.set(cache_key, json.dumps(coordinates.dict()), expire=3600)
        return coordinates
    else:
        raise ValueError("No results found for the given place name.")
