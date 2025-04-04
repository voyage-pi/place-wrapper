from fastapi import APIRouter

from app.handlers.fetch_places_handler import fetch_places
from app.models.fetch_places.request_models import PlacesRequest
from app.models.fetch_places.response_models import PlacesResponse

from app.handlers.get_photo_handler import get_photo
from app.models.get_photos.request_models import Photo_gRPC
from app.models.get_photos.response_models import Photo

router = APIRouter(prefix="/places", tags=["places"])

@router.post("/", response_model=PlacesResponse)
async def post_places(request: PlacesRequest):
    """
    Fetch places using the POST method with a JSON request body.
    """
    places = await fetch_places(request)
    return PlacesResponse(places=places)

@router.get("/photo", response_model=Photo)
async def get_photo_endpoint(request: Photo_gRPC):
    """
    Fetch a photo using the POST method with a JSON request body.
    """
    photo = await get_photo(request)
    return photo