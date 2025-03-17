import httpx
import os
from app.config.settings import RECOMMENDATION_SERVICE_URL

async def send_to_recommendation(normalized_data):
    """Send normalized place data to the recommendation service."""
    async with httpx.AsyncClient() as client:
        response = await client.post(RECOMMENDATION_SERVICE_URL, json={"places": normalized_data})
    
    return response.json()
