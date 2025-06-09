import httpx
import json

from app.models.get_place.response_model import GetPlaceResponse, PriceRange
from app.models.get_place.response_model import OpeningPeriod
from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client

BASE_GOOGLE_URL = "https://places.googleapis.com/v1/places"

async def get_place_info(place_id: str) -> GetPlaceResponse:
    """
    Get place information from Google Places API.
    """
    cache_key = f"place_info_{place_id}"
    cached_response = await redis_client.get(cache_key)

    if cached_response:
        print("FROM CACHE")
        return json.loads(cached_response)
    
    fields = (
        "id,displayName,location,rating,types,formattedAddress,priceLevel,"
        "currentOpeningHours,priceRange,nationalPhoneNumber,internationalPhoneNumber,photos,"
        "accessibilityOptions,regularOpeningHours,goodForChildren,"
        "goodForGroups,userRatingCount,editorialSummary,reviews"
    )
    url = f"{BASE_GOOGLE_URL}/{place_id}"
    params = {"fields": fields}
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    print("GOOGLE RESPONSE", data)

    normalized_data = normalize_place_response(data)

    await redis_client.set(cache_key, json.dumps(normalized_data), expire=3600)

    return normalized_data

def normalize_place_response(data):
    place = data.get("places", [{}])[0] if "places" in data else data.get("result", data)

    # Location
    location = None
    if "location" in place:
        loc = place["location"]
        location = {
            "latitude": loc.get("latitude"),
            "longitude": loc.get("longitude")
        }

    # Photos
    photos = []
    for photo in place.get("photos", []):
        photos.append({
            "name": photo.get("name"),
            "widthPx": photo.get("widthPx"),
            "heightPx": photo.get("heightPx"),
            "googleMapsUri": photo.get("googleMapsUri")
        })

    # Reviews
    reviews = []
    for review in place.get("reviews", []):
        # Extract text as string
        text = review.get("text")
        if isinstance(text, dict):
            text = text.get("text")
        # Try to parse time as int, else None
        try:
            time_val = int(review.get("relativePublishTimeDescription"))
        except (TypeError, ValueError):
            time_val = None
        reviews.append({
            "author_name": review.get("authorAttribution", {}).get("displayName"),
            "rating": review.get("rating"),
            "text": text,
            "time": time_val
        })

    # Opening Hours
    opening_hours = None
    periods = []
    # Prefer currentOpeningHours, fallback to regularOpeningHours
    hours = place.get("currentOpeningHours") or place.get("regularOpeningHours")
    if hours and "periods" in hours:
        for period in hours["periods"]:
            open_info = period.get("open", {})
            close_info = period.get("close", {})
            # Only keep int fields (day, hour, minute)
            open_clean = {k: v for k, v in open_info.items() if k in ("day", "hour", "minute") and isinstance(v, int)}
            close_clean = {k: v for k, v in close_info.items() if k in ("day", "hour", "minute") and isinstance(v, int)}
            periods.append(
                OpeningPeriod(
                    open=open_clean,
                    close=close_clean
                ).dict()
            )
        opening_hours = {
            "openNow": hours.get("openNow"),
            "periods": periods
        }
    # pricing range
    google_range=place.get("priceRange",None)
    if google_range is not None:
        print(google_range)
        start_price=int(google_range.get("startPrice").get("units"))
        end_price=int(google_range.get("endPrice").get("units"))
        currency=str(google_range.get("startPrice").get("currencyCode"))
        google_range=PriceRange(currency=currency,start_price=start_price,end_price=end_price).model_dump()
    return {
        "place_id": place.get("id"),
        "id": place.get("id"),
        "name": place.get("displayName", {}).get("text"),
        "description": place.get("editorialSummary", {}).get("overview"),
        "address": place.get("formattedAddress"),
        "phone_number": place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber"),
        "location": location,
        "types": place.get("types", []),
        "photos": photos,
        "rating": place.get("rating"),
        "reviews": reviews,
        "priceRange":google_range,
        "priceLevel":place.get("priceLevel"),
        "opening_hours": opening_hours
    }
    
    
