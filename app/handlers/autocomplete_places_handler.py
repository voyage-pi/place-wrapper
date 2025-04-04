import httpx
import json

from app.models.autocomplete_places.request_models import AutocompleteSearch
from app.models.autocomplete_places.response_models import Suggestion, Suggestions_List
from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client

BASE_GOOGLE_URL = "https://places.googleapis.com/v1/places:autocomplete"

async def autocomplete_places(request: AutocompleteSearch):
    """
    Autocomplete places from Google Places API.
    Normalizes the response before returning.
    """

    # Extract parameters from the request
    input_text = request.input

    # Generate a Redis cache key
    cache_key = f"autocomplete:{input_text}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print("FROM CACHE")
        return json.loads(cached_data)

    # Prepare API request headers
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
    }

    # Prepare request payload
    payload = {
        "input": input_text,
    }

    # Make the API request
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_GOOGLE_URL, json=payload, headers=headers)
        data = response.json()

    print("GOOGLE API RAW RESPONSE:", data)

    # Initialize the suggestions list
    suggestions = []

    # Normalize the response
    for item in data.get("suggestions", []):
        # Extract placePrediction data from each suggestion
        place_prediction = item.get("placePrediction", {})

        # Create the Suggestion model instance
        suggestion = Suggestion(
            place_id=place_prediction.get("placeId"),
            text=place_prediction.get("text", {}).get("text", ""),
            main_text=place_prediction.get("structuredFormat", {}).get("mainText", {}).get("text", ""),
            secondary_text=place_prediction.get("structuredFormat", {}).get("secondaryText", {}).get("text", ""),
        ) 
        
        # Append the suggestion to the list
        suggestions.append(suggestion)

    # Convert the suggestions to a list and cache the response
    suggestions_data = [suggestion.model_dump() for suggestion in suggestions]
    await redis_client.set(cache_key, json.dumps(suggestions_data), expire=3600)

    return suggestions
