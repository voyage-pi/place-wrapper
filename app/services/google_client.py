import httpx
import os
from services.redis_client import redis_client
from config.settings import GOOGLE_MAPS_API_KEY

BASE_GOOGLE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

async def fetch_places(location: str, radius: int = 500, keyword: str = ""):
    """Fetch places from Google Maps API."""
    
    cache_key = f"places:{location}:{radius}:{keyword}"
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        return cached_data  # Return cached result if available

    params = {
        "location": location,
        "radius": radius,
        "keyword": keyword,
        "key": GOOGLE_MAPS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_GOOGLE_URL, params=params)
        data = response.json()

    if "results" not in data:
        return {"error": "Invalid response from Google API", "details": data}

    normalized_data = normalize_google_response(data["results"])
    
    # Cache the result in Redis for 1 hour
    await redis_client.set(cache_key, normalized_data, expire=3600)

    return normalized_data

def normalize_google_response(places):
    """Normalize Google Places API response to a consistent format."""
    
    normalized = []
    for place in places:
        normalized.append({
            "id": place.get("place_id"),
            "name": place.get("name"),
            "location": place["geometry"]["location"] if "geometry" in place else None,
            "rating": place.get("rating"),
            "types": place.get("types"),
            "address": place.get("vicinity"),
            "price_level": place.get("price_level", None),
            "opening_hours": place.get("opening_hours", {}).get("open_now") if "opening_hours" in place else None
        })
    
    return normalized
