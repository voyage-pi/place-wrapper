from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class PlacePhoto(BaseModel):
    name: str
    widthPx: int
    heightPx: int
    googleMapsUri: Optional[str] = None


class AccessibilityOptions(BaseModel):
    wheelchairAccessibleParking: Optional[bool] = None
    wheelchairAccessibleEntrance: Optional[bool] = None
    wheelchairAccessibleRestroom: Optional[bool] = None
    wheelchairAccessibleSeating: Optional[bool] = None


class OpeningPeriod(BaseModel):
    open: Dict[str, int]  # Example: {"day": 1, "hour": 7, "minute": 30}
    close: Dict[str, int]


class OpeningHours(BaseModel):
    openNow: Optional[bool] = None
    periods: List[OpeningPeriod] = []


class PlaceResponse(BaseModel):
    ID: str
    name: Optional[str] = None
    location: Dict[str, float]  # {"latitude": 37.7749, "longitude": -122.4194}
    types: List[str]
    photos: List[PlacePhoto] = []
    accessibilityOptions: Optional[AccessibilityOptions] = None
    openingHours: Optional[OpeningHours] = None
    priceRange: Optional[Dict[str, Any]] = None
    rating: Optional[float] = None
    userRatingCount: Optional[int] = None
    internationalPhoneNumber: Optional[str] = None
    nationalPhoneNumber: Optional[str] = None
    allowsDogs: Optional[bool] = None
    goodForChildren: Optional[bool] = None
    goodForGroups: Optional[bool] = None


class PlacesResponse(BaseModel):
    places: List[PlaceResponse]
    nextPageToken: Optional[str] = None
