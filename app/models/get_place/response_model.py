from pydantic import BaseModel
from typing import Optional, Dict, List

class PlacePhoto(BaseModel):
    name: str
    widthPx: int
    heightPx: int
    googleMapsUri: Optional[str] = None

class OpeningPeriod(BaseModel):
    open: Dict[str, int]  # Example: {"day": 1, "hour": 7, "minute": 30}
    close: Dict[str, int]

class OpeningHours(BaseModel):
    openNow: Optional[bool] = None
    periods: List[OpeningPeriod] = []

class Review(BaseModel):
    author_name: Optional[str] = None
    rating: Optional[float] = None
    text: Optional[str] = None
    time: Optional[int] = None

class Location(BaseModel):
    latitude: float
    longitude: float

class GetPlaceResponse(BaseModel):
    place_id: str
    name: Optional[str] = None
    description: Optional[str] = None  # from editorial_summary.overview
    address: Optional[str] = None      # formatted_address
    phone_number: Optional[str] = None # formatted_phone_number
    location: Optional[Location] = None
    types: Optional[List[str]] = None
    photos: Optional[List[PlacePhoto]] = []
    rating: Optional[float] = None
    reviews: Optional[List[Review]] = None
    opening_hours: Optional[OpeningHours] = None