"""
Utilities for handling Google Fonts in the application
"""
import random
from typing import Dict, List, Optional

# Google Fonts combinations for different themes
FONT_COMBINATIONS = {
    "Classic": {
        "title": "Playfair Display",
        "body": "Source Sans Pro",
        "url": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@400;600&display=swap"
    },
    "Modern": {
        "title": "Roboto",
        "body": "Open Sans",
        "url": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Open+Sans:wght@400;600&display=swap"
    },
    "Elegant": {
        "title": "Cormorant Garamond",
        "body": "Lato",
        "url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&family=Lato:wght@400;700&display=swap"
    }
}

# Additional font combinations for variety
ADDITIONAL_COMBINATIONS = [
    {
        "title": "Merriweather",
        "body": "Roboto",
        "url": "https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Roboto:wght@400;500&display=swap"
    },
    {
        "title": "Lora",
        "body": "Open Sans",
        "url": "https://fonts.googleapis.com/css2?family=Lora:wght@400;700&family=Open+Sans:wght@400;600&display=swap"
    }
]

def download_google_fonts(theme: Optional[str] = None) -> Dict[str, str]:
    """
    Get a font combination for the card, either based on theme or randomly.
    
    Args:
        theme: Optional theme name to get specific fonts
        
    Returns:
        Dict containing title font, body font, and Google Fonts URL
    """
    if theme and theme in FONT_COMBINATIONS:
        return FONT_COMBINATIONS[theme]
    
    # If no theme specified or theme not found, return random combination
    all_combinations = list(FONT_COMBINATIONS.values()) + ADDITIONAL_COMBINATIONS
    return random.choice(all_combinations)

def get_available_fonts() -> List[Dict[str, str]]:
    """
    Get list of all available font combinations.
    
    Returns:
        List of dictionaries containing font information
    """
    return list(FONT_COMBINATIONS.values()) + ADDITIONAL_COMBINATIONS 