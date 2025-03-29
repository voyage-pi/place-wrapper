from fastapi import APIRouter, Query, Body
from app.services.google_client import fetch_places

router = APIRouter(prefix="/places", tags=["places"])

@router.post("/")
async def post_places(request: dict = Body(...)):
    """
    Fetch places using the POST method with a JSON request body.
    """
    places = await fetch_places(request)
    return {"response": places}
