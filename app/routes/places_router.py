from fastapi import APIRouter

from app.handlers.fetch_places_handler import fetch_places
from app.models.fetch_places.request_models import PlacesRequest
from app.models.fetch_places.response_models import PlacesResponse

router = APIRouter(prefix="/places", tags=["places"])

@router.post("/", response_model=PlacesResponse)
async def post_places(request: PlacesRequest):
    """
    Fetch places using the POST method with a JSON request body.
    """
    places = await fetch_places(request)
    return PlacesResponse(places=places)
