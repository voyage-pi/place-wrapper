import httpx
import json

from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client  # Import Redis client

BASE_GOOGLE_URL = "https://places.googleapis.com/v1/places:searchNearby"

async def fetch_places(request: dict):
    """
    Fetch places from Google Places API with all required fields.
    Normalizes the response before returning.
    """

    # Extract parameters from request
    location = request.get("location", {})
    latitude = float(location.get("latitude", 0))
    longitude = float(location.get("longitude", 0))
    radius = int(request.get("radius", 500))
    included_types = request.get("includedTypes", [])
    excluded_types = request.get("excludedTypes", [])

    # Validate request
    if not latitude or not longitude:
        return {"error": "Latitude and Longitude are required"}
    if set(included_types) & set(excluded_types):
        return {"error": "A place type cannot be both included and excluded"}

    # Generate a Redis cache key
    cache_key = f"places:{latitude}:{longitude}:{radius}:{','.join(included_types)}:{','.join(excluded_types)}"
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
            "places.allowsDogs,places.goodForChildren,places.goodForGroups"
        ),
    }

    # Prepare request payload
    payload = {
        "includedTypes": included_types,
        "excludedTypes": excluded_types,
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius,
            }
        },
    }

    # Make request to Google API
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_GOOGLE_URL, json=payload, headers=headers)
        data = response.json()

    print("GOOGLE API RAW RESPONSE:", json.dumps(data, indent=2))

    # Validate API response
    if "places" not in data:
        return {"error": "Invalid response from Google API", "details": data}

    # Normalize response
    normalized_data = normalize_google_response(data["places"])

    # Cache the normalized response in Redis for 1 hour
    await redis_client.set(cache_key, json.dumps(normalized_data), expire=3600)

    return normalized_data


def normalize_google_response(places):
    """
    Normalize Google Places API response to match required fields.
    """

    normalized = []

    for place in places:
        opening_hours = {}

        # Process opening hours if available
        if "currentOpeningHours" in place and "periods" in place["currentOpeningHours"]:
            day_mapping = {
                0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
                4: "Thursday", 5: "Friday", 6: "Saturday",
            }
            for period in place["currentOpeningHours"]["periods"]:
                day = day_mapping.get(period["open"]["day"])
                open_time = f'{period["open"]["hour"]:02}:{period["open"]["minute"]:02}'
                close_time = f'{period["close"]["hour"]:02}:{period["close"]["minute"]:02}'

                opening_hours[day] = {"open": open_time, "close": close_time}

        # Process regular opening hours
        regular_opening_hours = place.get("regularOpeningHours", {}).get("weekdayDescriptions", [])

        # Process photos
        photos = [photo.get("name") for photo in place.get("photos", [])]

        # Process accessibility options
        accessibility_options = place.get("accessibilityOptions", {})

        normalized.append({
            "ID": place.get("id"),
            "name": place.get("displayName", {}).get("text"),
            "location": place.get("location"),
            "types": place.get("types", []),
            "photos": photos,
            "accessibilityOptions": accessibility_options,
            "OpeningHours": {
                "openNow": place.get("currentOpeningHours", {}).get("openNow"),
                "periods": opening_hours,
            },
            "priceRange": place.get("priceLevel", "UNKNOWN"),
            "rating": place.get("rating"),
            "internationalPhoneNumber": place.get("internationalPhoneNumber"),
            "nationalPhoneNumber": place.get("nationalPhoneNumber"),
            "allowsDogs": place.get("allowsDogs"),
            "goodForChildren": place.get("goodForChildren"),
            "goodForGroups": place.get("goodForGroups")
        })

    return {"places": normalized}

