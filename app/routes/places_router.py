from fastapi import APIRouter

from app.handlers.fetch_places_handler import fetch_places
from app.models.fetch_places.request_models import PlacesRequest
from app.models.fetch_places.response_models import PlacesResponse

from app.handlers.get_photo_handler import get_photo
from app.models.get_photos.request_models import Photo_gRPC
from app.models.get_photos.response_models import Photo

from app.handlers.autocomplete_places_handler import autocomplete_places
from app.models.autocomplete_places.request_models import AutocompleteSearch
from app.models.autocomplete_places.response_models import Suggestions_List
from app.models.fetch_places.response_models import PlaceResponse

router = APIRouter(prefix="/places", tags=["places"])


@router.post("/", response_model=PlacesResponse)
async def post_places(request: PlacesRequest):
    """
    Fetch places using the POST method with a JSON request body.
    """
    places: list[PlaceResponse] = await fetch_places(request)
    return PlacesResponse(places=places)

@router.post("/photo", response_model=Photo)
async def get_photo_endpoint(request: Photo_gRPC):
    """
    Fetch a photo using the POST method with a JSON request body.
    """
    photo = await get_photo(request)
    return photo


@router.post("/autocomplete", response_model=Suggestions_List)
async def autocomplete_search(request: AutocompleteSearch):
    """
    Autocomplete places using the GET method.
    """
    suggestions = await autocomplete_places(request)
    return Suggestions_List(suggestions_list=suggestions)
