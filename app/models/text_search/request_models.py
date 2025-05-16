from pydantic import BaseModel, Field

class TextSearchRequest(BaseModel):
    query: str = Field(..., description="The search query string")
    radius: int = Field(5000, description="Search radius in meters")
    location: dict = Field(
        ..., 
        description="The location to search around", 
        example={"latitude": 40.7128, "longitude": -74.0060}
    ) 