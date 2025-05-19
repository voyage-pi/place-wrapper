import httpx
import json
from app.models.get_place.response_model import PriceRange
from app.models.fetch_places.request_models import PlacesRequest
from app.models.fetch_places.response_models import (
    PlaceResponse,
    OpeningHours,
    OpeningPeriod,
    PlacePhoto,
    AccessibilityOptions,
)
from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client

BASE_GOOGLE_URL = "https://places.googleapis.com/v1/places:searchNearby"


async def fetch_places(
    request: PlacesRequest,
) -> list[PlaceResponse] | tuple[list[PlaceResponse], str]:
    """
    Fetch places from Google Places API with all required fields.
    Normalizes the response before returning.
    """

    # Extract parameters from request (use attributes instead of .get())
    latitude = request.location.latitude
    longitude = request.location.longitude
    radius = request.radius
    included_types = request.includedTypes
    excluded_types = request.excludedTypes

    # Validate request
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
            "places.internationalPhoneNumber,places.priceRange,places.photos,"
            "places.accessibilityOptions,places.regularOpeningHours,"
            "places.allowsDogs,places.goodForChildren,places.goodForGroups,"
            "places.userRatingCount"
        ),
    }

    payload = {
        "includedTypes": included_types,
        "excludedPrimaryTypes": excluded_types,
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

    # Validate API response
    if "places" not in data:
        return {"error": "Invalid response from Google API", "details": data}

    # Normalize response
    normalized_data = normalize_google_response(data["places"])

    # Cache the normalized response in Redis for 1 hour
    await redis_client.set(
        cache_key,
        json.dumps([place.model_dump() for place in normalized_data]),
        expire=3600,
    )

    next_page_token = data.get("next_page_token", None)
    if next_page_token:
        return [place.model_dump() for place in normalized_data], next_page_token
    return [place.model_dump() for place in normalized_data]


def normalize_google_response(places):
    """
    Normalize Google Places API response to match required fields.
    """

    normalized = []

    for place in places:
        opening_hours = []

        if "currentOpeningHours" in place and "periods" in place["currentOpeningHours"]:
            for period in place["currentOpeningHours"]["periods"]:
                opening_hours.append(
                    OpeningPeriod(
                        open={
                            "day": period["open"]["day"],
                            "hour": period["open"]["hour"],
                            "minute": period["open"]["minute"],
                        },
                        close={
                            "day": period["close"]["day"],
                            "hour": period["close"]["hour"],
                            "minute": period["close"]["minute"],
                        },
                    )
                )

        photos = [PlacePhoto(**photo) for photo in place.get("photos", [])]

        accessibility_options = AccessibilityOptions(
            **place.get("accessibilityOptions", {})
        )

        # pricing range
        google_range=place.get("priceRange",None)
        if google_range is not None:
            print(google_range)
            start_price=int(google_range.get("startPrice").get("units"))
            # when a place is $100+ i just set the end_price to 500$ for limitations and type structure purposes
            end_price=int(google_range.get("endPrice",{"units":500}).get("units"))
            currency=str(google_range.get("startPrice").get("currencyCode"))
            google_range=PriceRange(currency=currency,start_price=start_price,end_price=end_price).model_dump()

        normalized.append(
            PlaceResponse(
                ID=place.get("id"),
                name=place.get("displayName", {}).get("text"),
                location={
                    "latitude": place["location"]["latitude"],
                    "longitude": place["location"]["longitude"],
                },
                types=place.get("types", []),
                photos=photos,
                accessibilityOptions=accessibility_options,
                OpeningHours=OpeningHours(
                    openNow=place.get("currentOpeningHours", {}).get("openNow"),
                    periods=opening_hours,
                ),
                priceLevel=place.get("priceLevel"),
                priceRange=google_range,
                rating=place.get("rating"),
                userRatingCount=place.get("userRatingCount"),
                internationalPhoneNumber=place.get("internationalPhoneNumber"),
                nationalPhoneNumber=place.get("nationalPhoneNumber"),
                allowsDogs=place.get("allowsDogs", False),
                goodForChildren=place.get("goodForChildren", False),
                goodForGroups=place.get("goodForGroups", False),
            )
        )
        print(normalized)
    return normalized
