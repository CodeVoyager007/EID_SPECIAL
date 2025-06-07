"""
Helper functions for card styling and theme management
"""
from typing import Dict, List, Tuple
import random

def style_card(theme: str) -> Dict[str, str]:
    """
    Get styling properties for a specific card theme
    """
    themes = {
        "Classic": {
            "font_family": "'Playfair Display', serif",
            "color": "#1a1a1a",
            "background": "#ffffff"
        },
        "Modern": {
            "font_family": "'Roboto', sans-serif",
            "color": "#333333",
            "background": "#f5f5f5"
        },
        "Elegant": {
            "font_family": "'Cormorant Garamond', serif",
            "color": "#2c3e50",
            "background": "#ecf0f1"
        }
    }
    return themes.get(theme, themes["Classic"])

def get_random_font_combination() -> Tuple[str, str]:
    """
    Get a random combination of heading and body fonts
    """
    heading_fonts = [
        "Playfair Display",
        "Cormorant Garamond",
        "Lora",
        "Merriweather"
    ]
    
    body_fonts = [
        "Source Sans Pro",
        "Open Sans",
        "Roboto",
        "Lato"
    ]
    
    return (random.choice(heading_fonts), random.choice(body_fonts))

def get_available_themes() -> List[str]:
    """
    Get list of available card themes
    """
    return ["Classic", "Modern", "Elegant"] 