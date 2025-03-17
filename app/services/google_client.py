import httpx
import json
from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client  # Import Redis client

BASE_GOOGLE_URL = "https://places.googleapis.com/v1/places:searchNearby"

async def fetch_places(location: str, radius: int = 500, keyword: str = ""):
    """Fetch places from Google Places API (New API Version) with caching."""
    
    lat, lng = map(float, location.split(","))

    # Generate cache key
    cache_key = f"places:{lat}:{lng}:{radius}:{keyword}"
    cached_data = await redis_client.get(cache_key)

    # Return cached data if available
    if cached_data:
        print("FROM CACHE")
        return json.loads(cached_data)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY, 
        "X-Goog-FieldMask": "places.id,places.displayName,places.location,places.rating,places.types,places.formattedAddress,places.priceLevel,places.currentOpeningHours"
    }

    payload = {
        "includedTypes": ["point_of_interest", "establishment"],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius
            }
        }
    }

    if keyword:
        payload["includedTypes"] = [keyword]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            BASE_GOOGLE_URL,
            json=payload,
            headers=headers
        )
        data = response.json()

    print("GOOGLE API RAW RESPONSE:", json.dumps(data, indent=2))

    if "places" not in data:
        return {"error": "Invalid response from Google API", "details": data}

    normalized_data = normalize_google_response(data["places"])

    # Cache the normalized response in Redis for 1 hour
    await redis_client.set(cache_key, json.dumps(normalized_data), expire=3600)

    return normalized_data

def normalize_google_response(places):
    """Normalize Google Places API response to a consistent format."""
    
    normalized = []
    
    for place in places:
        opening_hours = {}

        # Process opening hours if available
        if "currentOpeningHours" in place and "periods" in place["currentOpeningHours"]:
            for period in place["currentOpeningHours"]["periods"]:
                day = period["open"]["day"]
                open_time = f'{period["open"]["hour"]:02}:{period["open"]["minute"]:02}'
                close_time = f'{period["close"]["hour"]:02}:{period["close"]["minute"]:02}'
                
                opening_hours[day] = {
                    "open": open_time,
                    "close": close_time
                }

        normalized.append({
            "id": place.get("id"),
            "name": place.get("displayName", {}).get("text"),
            "location": place.get("location"),
            "rating": place.get("rating", None),
            "types": place.get("types", []),
            "address": place.get("formattedAddress", None),
            "price_level": place.get("priceLevel", None),
            "opening_hours": opening_hours  # Normalized opening hours
        })
    
    return normalized
