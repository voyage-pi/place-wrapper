import httpx
import json

from app.models.text_search.request_models import TextSearchRequest
from app.models.fetch_places.response_models import (
    PlaceResponse,
    OpeningHours,
    OpeningPeriod,
    PlacePhoto,
    AccessibilityOptions,
)
from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client
from app.handlers.fetch_places_handler import normalize_google_response

BASE_GOOGLE_URL = "https://places.googleapis.com/v1/places:searchText"

async def text_search(request: TextSearchRequest) -> list[PlaceResponse]:
    """
    Search places using text query from Google Places API.
    Normalizes the response before returning.
    """
    
    # Extract parameters from request
    query = request.query
    latitude = request.location["latitude"]
    longitude = request.location["longitude"]
    radius = request.radius
    
    # Generate a Redis cache key
    cache_key = f"text_search:{query}:{latitude}:{longitude}:{radius}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print("FROM CACHE")
        return json.loads(cached_data)
    
    # Prepare API request headers
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.location,places.rating,"
            "places.types,places.formattedAddress,places.priceLevel,"
            "places.currentOpeningHours,places.nationalPhoneNumber,"
            "places.internationalPhoneNumber,places.photos,"
            "places.accessibilityOptions,places.regularOpeningHours,"
            "places.allowsDogs,places.goodForChildren,places.goodForGroups,"
            "places.userRatingCount"
        ),
    }
    
    # Prepare request payload
    payload = {
        "textQuery": query,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius
            }
        }
    }
    
    # Make request to Google API
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_GOOGLE_URL, json=payload, headers=headers)
        data = response.json()
    
    # Validate API response
    if "places" not in data:
        return []
    
    # Normalize response
    normalized_data = normalize_google_response(data["places"])
    
    # Cache the normalized response in Redis for 1 hour
    await redis_client.set(
        cache_key,
        json.dumps([place.model_dump() for place in normalized_data]),
        expire=3600,
    )
    
    return [place.model_dump() for place in normalized_data] 