from pydantic import BaseModel

class Photo_gRPC(BaseModel):
    gRPC: str
    maxWidthPx: int = 300
    maxHeightPx: int = 300