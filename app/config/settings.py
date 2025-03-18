import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")