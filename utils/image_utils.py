"""
Utility functions for handling images in the Eid Card Generator.
"""
import os
import random
import requests
from loguru import logger
from typing import Optional, List

# Background categories with their search terms
BACKGROUND_CATEGORIES = [
    "Eid Moon & Stars",
    "Mosque Architecture",
    "Islamic Patterns",
    "Eid Celebration",
    "Lanterns & Lights",
    "Calligraphy Art",
    "Geometric Patterns",
    "Nature & Flowers"
]

SEARCH_TERMS = {
    "Eid Moon & Stars": ["crescent moon night", "eid moon", "ramadan moon stars", "night sky mosque"],
    "Mosque Architecture": ["grand mosque", "islamic architecture", "beautiful mosque", "mosque interior"],
    "Islamic Patterns": ["islamic pattern", "arabic pattern", "islamic geometric", "islamic art"],
    "Eid Celebration": ["eid celebration", "eid decoration", "eid festival", "eid lights"],
    "Lanterns & Lights": ["ramadan lanterns", "islamic lanterns", "moroccan lamps", "oriental lights"],
    "Calligraphy Art": ["islamic calligraphy", "arabic calligraphy", "islamic art", "arabic script art"],
    "Geometric Patterns": ["geometric pattern", "moroccan pattern", "islamic geometry", "arabesque pattern"],
    "Nature & Flowers": ["islamic garden", "arabic floral", "islamic floral", "moroccan garden"]
}

def get_pexels_image(category: str) -> Optional[str]:
    """
    Get a random image URL from Pexels API based on the category.
    """
    try:
        api_key = os.getenv("PEXELS_API_KEY")
        if not api_key:
            logger.error("PEXELS_API_KEY not found in environment variables")
            return None

        headers = {"Authorization": api_key}
        
        # Get search terms for the category
        search_terms = SEARCH_TERMS.get(category, SEARCH_TERMS["Islamic Patterns"])
        
        # Try each search term until we find a suitable image
        for search_term in search_terms:
            # Search parameters
            params = {
                "query": search_term,
                "orientation": "landscape",
                "size": "large",
                "per_page": 20,
                "min_width": 1200, 
                "min_height": 800
            }
            
            # Make API request
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we got any results
            if data.get("total_results", 0) > 0:
                photos = data.get("photos", [])
                if photos:
                    # Filter for high-quality images
                    quality_photos = [
                        p for p in photos 
                        if p["width"] >= 1200 and p["height"] >= 800
                    ]
                    if quality_photos:
                        chosen_photo = random.choice(quality_photos)
                        return chosen_photo["src"]["large2x"]
        
        # If no results found, try fallback categories
        fallback_categories = ["Islamic Patterns", "Geometric Patterns", "Nature & Flowers"]
        for category in fallback_categories:
            for search_term in SEARCH_TERMS[category]:
                params["query"] = search_term
                response = requests.get(
                    "https://api.pexels.com/v1/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                if data.get("total_results", 0) > 0:
                    photos = data.get("photos", [])
                    if photos:
                        chosen_photo = random.choice(photos)
                        return chosen_photo["src"]["large2x"]
        
        # If still no results, return None
        logger.warning("No images found on Pexels for any search terms")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching image from Pexels: {str(e)}")
        return None 