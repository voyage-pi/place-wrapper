from pydantic import BaseModel
from typing import List, Optional


class Location(BaseModel):
    latitude: float
    longitude: float


class PlacesRequest(BaseModel):
    type: str = "place"
    location: Location
    radius: int = 500
    includedTypes: Optional[List[str]] = []
    excludedTypes: Optional[List[str]] = []
