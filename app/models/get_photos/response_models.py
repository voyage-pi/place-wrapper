from pydantic import BaseModel

class Photo(BaseModel):
    name: str
    uri: str