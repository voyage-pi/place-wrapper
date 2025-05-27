import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLEMAPSAPIKEY")

if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY is not set in the environment variables.")
