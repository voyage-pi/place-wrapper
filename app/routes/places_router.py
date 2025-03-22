from fastapi import APIRouter

from app.services.google_client import fetch_places
from app.models.request_models import PlacesRequest
from app.models.response_models import PlacesResponse

router = APIRouter(prefix="/places", tags=["places"])

@router.post("/", response_model=PlacesResponse)
async def post_places(request: PlacesRequest):
    """
    Fetch places using the POST method with a JSON request body.
    """
    places = await fetch_places(request)
    return PlacesResponse(places=places)
