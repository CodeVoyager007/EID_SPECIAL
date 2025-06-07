"""
AI agents for the EidiCard generator.
"""
from typing import Dict, Optional, List
import litellm
from loguru import logger
from pydantic import BaseModel
import random
import os

# Configure LiteLLM to use OpenRouter
litellm.set_verbose = False
litellm.api_base = "https://openrouter.ai/api/v1/chat/completions"

# Default message if AI fails
DEFAULT_MESSAGE = """
May this Eid bring you joy, peace, and prosperity! 🌙✨
Wishing you and your family a blessed celebration filled with love, laughter, and cherished moments together.
May Allah accept our prayers and grant us His infinite mercy. 
عید مبارک
"""

# Emoji sets by tone
EMOJI_SETS = {
    "funny": ["😄", "🎉", "🎊", "🥳", "😊", "😃", "🤗", "🌟", "✨", "💫"],
    "emotional": ["❤️", "🤗", "💝", "💖", "🌟", "💕", "💗", "✨", "💫", "💓"],
    "religious": ["🕌", "☪️", "🌙", "✨", "🤲", "📿", "🌟", "💫", "🌺", "🌸"],
    "formal": ["🌺", "🎀", "✨", "💫", "🌸", "🌹", "🌷", "🎗️", "🌟", "💐"]
}

def generate_eid_message(
    recipient: str,
    tone: str = "formal",
    sender: str = "",
    include_hadith: bool = False,
    include_urdu: bool = False,
    include_emojis: bool = True
) -> str:
    """
    Generate a personalized Eid greeting message.
    
    Args:
        recipient: Name of the recipient
        tone: Message tone (funny, emotional, religious, formal)
        sender: Name of the sender
        include_hadith: Whether to include a Hadith
        include_urdu: Whether to include Urdu text
        include_emojis: Whether to include emojis
        
    Returns:
        str: Generated Eid greeting message
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return DEFAULT_MESSAGE
        
    eid_agent = EidAgent(api_key)
    message_agent = MessageCraftAgent(eid_agent)
    
    preferences = {
        "include_hadith": include_hadith,
        "include_urdu": include_urdu,
        "include_emojis": include_emojis,
        "emoji_count": 2 if include_emojis else 0,
        "sender": sender
    }
    
    return message_agent.craft_message(recipient, tone, preferences)

class EidAgent:
    def __init__(self, api_key: str):
        """
        Initialize the Eid card generation agent.
        
        Args:
            api_key: OpenRouter API key
        """
        self.api_key = api_key
        litellm.api_key = api_key
        # Using Mistral's latest model from OpenRouter
        self.model = "openrouter/mistral-7b-instruct"
        self.conversation_history = []
    
    def _get_completion(self, prompt: str) -> str:
        """
        Get completion from the LLM.
        """
        try:
            messages = [
                {
                    "role": "system", 
                    "content": """You are an expert at crafting personalized Eid greetings. 
                    Your task is to generate warm, culturally appropriate Eid messages.
                    Always include warm wishes, blessings, and maintain the specified tone.
                    Make messages personal and heartfelt."""
                },
                {"role": "user", "content": prompt}
            ]
            
            response = litellm.completion(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                headers={
                    "HTTP-Referer": "https://localhost:8501",
                    "X-Title": "EidiCard Generator"
                }
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            # Return a default message instead of error message
            return DEFAULT_MESSAGE

    def generate_greeting(
        self,
        recipient: str,
        tone: str,
        include_hadith: bool = False,
        include_urdu: bool = False,
        emoji_count: int = 2,
        sender: str = ""
    ) -> str:
        """
        Generate a personalized Eid greeting.
        """
        prompt = f"""
        Generate a heartfelt Eid greeting message for {recipient}.
        
        Requirements:
        - Tone should be: {tone}
        - Include Hadith: {include_hadith}
        - Include Urdu: {include_urdu}
        - Sender name: {sender if sender else "Not specified"}
        
        Guidelines:
        - Make it personal and warm
        - Keep it appropriate for the specified tone
        - If including Hadith, use a relevant one about Eid, celebration, or giving
        - If including Urdu, add 'Eid Mubarak' in Urdu script (عید مبارک)
        - Length should be 2-3 paragraphs
        - Add appropriate line breaks for readability
        - Do not include any emojis in the response
        """
        
        response = self._get_completion(prompt)
        
        # Add emojis if requested
        if emoji_count > 0 and tone in EMOJI_SETS:
            # Select random emojis from the tone's set
            emojis = random.sample(EMOJI_SETS[tone], min(emoji_count, len(EMOJI_SETS[tone])))
            emoji_str = " ".join(emojis)
            # Add emojis at start and end
            response = f"{emoji_str}\n{response}\n{emoji_str}"
        
        return response

    def suggest_theme(self, tone: str, message: str) -> str:
        """
        Suggest an appropriate theme based on the message tone and content.
        """
        prompt = f"""
        Based on the following message tone and content, suggest the most appropriate theme
        from these options: classic, modern, elegant
        
        Tone: {tone}
        Message: {message}
        
        Reply with just the theme name in lowercase.
        """
        
        theme = self._get_completion(prompt).strip().lower()
        return theme if theme in ["classic", "modern", "elegant"] else "classic"

    def enhance_message(self, message: str, tone: str) -> str:
        """
        Enhance a message with appropriate emojis and formatting.
        """
        prompt = f"""
        Enhance this Eid greeting message with appropriate emojis and formatting.
        Keep the tone {tone}.
        Add emojis tastefully without overwhelming the message.
        
        Message: {message}
        
        Return the enhanced message with emojis placed naturally.
        """
        
        enhanced = self._get_completion(prompt)
        return enhanced if enhanced != DEFAULT_MESSAGE else message

class MessageCraftAgent:
    def __init__(self, eid_agent: EidAgent):
        self.eid_agent = eid_agent
    
    def craft_message(
        self,
        recipient: str,
        tone: str,
        preferences: Dict[str, bool]
    ) -> str:
        """
        Craft a personalized Eid message.
        """
        return self.eid_agent.generate_greeting(
            recipient=recipient,
            tone=tone,
            include_hadith=preferences.get("include_hadith", False),
            include_urdu=preferences.get("include_urdu", False),
            emoji_count=preferences.get("emoji_count", 2) if preferences.get("include_emojis", True) else 0,
            sender=preferences.get("sender", "")
        )

class StyleAgent:
    def __init__(self, eid_agent: EidAgent):
        self.eid_agent = eid_agent
    
    def get_theme(self, tone: str, message: str) -> str:
        """
        Get an appropriate theme for the message.
        """
        return self.eid_agent.suggest_theme(tone, message) 