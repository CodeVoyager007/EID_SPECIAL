"""
Utility functions for image handling and Pexels API integration
"""
import os
import requests
import random
import time
from typing import Optional, Dict, Any, List
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKGROUND_CATEGORIES = [
    "islamic architecture",
    "mosque",
    "islamic patterns",
    "ramadan",
    "eid celebration",
    "lanterns",
    "crescent moon",
    "islamic art"
]

def get_pexels_image(query: str, api_key: Optional[str] = None, max_retries: int = 3) -> Optional[str]:
    """
    Fetch a random image URL from Pexels API based on the query
    
    Args:
        query: Search term for the image
        api_key: Optional Pexels API key (will use PEXELS_API_KEY from env if not provided)
        max_retries: Number of retries for failed requests
        
    Returns:
        Optional[str]: Image URL or None if failed
    """
    # Get API key from environment if not provided
    api_key = api_key or os.getenv('PEXELS_API_KEY')
    if not api_key:
        raise ValueError("Pexels API key not found. Please set PEXELS_API_KEY in your .env file")
    
    headers = {"Authorization": api_key}
    base_url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "per_page": 20,
        "orientation": "landscape"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("photos"):
                return None
            
            photo = random.choice(data["photos"])
            return photo["src"]["large2x"]  # Return the URL directly
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)
    
    return None

from utils.pdf_generator import create_pdf, create_preview 