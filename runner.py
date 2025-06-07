"""
Runner module for managing agent execution flow.
"""
from typing import Dict, Optional, Tuple
import os
from pathlib import Path
import tempfile

from agents import EidAgent, MessageCraftAgent, StyleAgent
from tools import style_card
from utils.pdf_generator import create_pdf, create_preview

class EidCardRunner:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the EidCard generation runner.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        # Initialize agents
        self.eid_agent = EidAgent(self.api_key)
        self.message_agent = MessageCraftAgent(self.eid_agent)
        self.style_agent = StyleAgent(self.eid_agent)
    
    def generate_card(
        self,
        recipient: str,
        tone: str,
        preferences: Dict[str, bool],
        shape: str = "rectangle",
        output_path: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Generate an Eid greeting card.
        
        Args:
            recipient: Name of the recipient
            tone: Desired tone of the message
            preferences: Dict of preferences (include_hadith, include_urdu, include_emojis, emoji_count, colors)
            shape: Shape of the card (rectangle, circle, heart, etc.)
            output_path: Optional path to save the PDF
        
        Returns:
            Tuple of (message, preview_html, pdf_path)
        """
        # Generate message
        message = self.message_agent.craft_message(
            recipient=recipient,
            tone=tone,
            preferences=preferences
        )
        
        # Get theme and apply custom colors
        theme_name = self.style_agent.get_theme(tone, message)
        theme = style_card(theme_name, shape)
        
        # Override theme colors with user preferences if provided
        if "colors" in preferences:
            theme.update(preferences["colors"])
        
        # Create preview
        preview_html = create_preview(
            message=message,
            recipient=recipient,
            theme=theme
        )
        
        # Generate PDF
        pdf_path = create_pdf(
            message=message,
            recipient=recipient,
            theme=theme,
            output_path=output_path
        )
        
        return message, preview_html, pdf_path
    
    def get_conversation_history(self) -> list:
        """
        Get the conversation history from the EidAgent.
        """
        return self.eid_agent.conversation_history 