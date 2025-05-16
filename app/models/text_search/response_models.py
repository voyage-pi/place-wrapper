from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.fetch_places.response_models import PlaceResponse

class TextSearchResponse(BaseModel):
    places: List[PlaceResponse] = Field(
        default=[], 
        description="List of places matching the text search query"
    ) 