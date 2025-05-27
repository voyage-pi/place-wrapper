from fastapi import APIRouter

from app.handlers.search_coordinates_handler import search_coordinates
from app.models.search_coordinates.request_models import PlaceName
from app.models.search_coordinates.response_models import Location

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=Location)
async def get_coordinates(request: PlaceName):
    """
    Fetch places using the POST method with a JSON request body.
    """
    coordinates = await search_coordinates(request)

    return coordinates

