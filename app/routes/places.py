from fastapi import APIRouter, Query
from services.google_client import fetch_places
from services.forward_service import send_to_recommendation

router = APIRouter()

@router.get("/places/")
async def get_places(
    location: str = Query(..., description="Latitude,Longitude"),
    radius: int = Query(500, description="Search radius in meters"),
    keyword: str = Query("", description="Optional keyword to filter places")
):
    """Fetch and normalize Google Places API response."""
    places = await fetch_places(location, radius, keyword)
    await send_to_recommendation(places)  # Forward to recommendation service
    return {"normalized_places": places}
