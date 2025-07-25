"""Configuration settings for SchoolConnect MCP Server."""

import os
import logging
from typing import Optional, Set
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Configuration settings loaded from environment variables.
    
    This class manages all configuration for the MCP server, including:
    - Airtable database connection settings
    - OpenAI API configuration
    - Calendar integration settings
    - Search and filtering parameters
    """
    
    def __init__(self):
        # Airtable Configuration
        self.AIRTABLE_API_KEY: str = os.getenv("AIRTABLE_API_KEY", "")
        self.AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
        
        # OpenAI Configuration  
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        
        # Calendar Integration (n8n webhook)
        self.N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "")
        
        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        
        # Default Settings for Announcements
        self.DEFAULT_ANNOUNCEMENT_LIMIT: int = 15
        self.MAX_ANNOUNCEMENT_LIMIT: int = 50
        
        # Calendar Event Settings
        self.DEFAULT_EVENT_DURATION_HOURS: int = 1
        self.DEFAULT_EVENT_START_TIME: str = "09:00"
        self.REMINDER_DAYS_BEFORE: int = 3
        
        # Search Algorithm Configuration
        # Stop words are common words that should be filtered out during search
        # to prevent false matches (e.g., searching for "and" would match everything)
        self.STOP_WORDS: Set[str] = {
            # Articles
            'a', 'an', 'the',
            # Conjunctions  
            'and', 'or', 'but', 'nor', 'for', 'so', 'yet',
            # Prepositions
            'at', 'by', 'for', 'from', 'in', 'of', 'on', 'to', 'with',
            # Pronouns
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            # Common verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'shall',
            # Question words
            'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how',
            # Quantifiers
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'now'
        }
        
        # Time-related keywords that indicate timed events (not all-day)
        self.TIME_INDICATORS: Set[str] = {
            'morning', 'afternoon', 'evening', 'noon', 'midnight',
            'breakfast', 'lunch', 'dinner', 'snack',
            'am', 'pm', 'a.m.', 'p.m.',
            'early', 'late', 'before', 'after'
        }
    
    def validate(self) -> None:
        """Validate that all required settings are present.
        
        Raises:
            ValueError: If any required environment variables are missing.
        """
        required_settings = [
            ("AIRTABLE_API_KEY", self.AIRTABLE_API_KEY),
            ("AIRTABLE_BASE_ID", self.AIRTABLE_BASE_ID),
            ("OPENAI_API_KEY", self.OPENAI_API_KEY),
        ]
        
        missing = [name for name, value in required_settings if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please check your .env file and ensure all required values are set."
            )
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            self.LOG_LEVEL = 'INFO'
    
    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_airtable_config(self) -> dict:
        """Get Airtable configuration as a dictionary.
        
        Returns:
            dict: Airtable configuration with api_key and base_id.
        """
        return {
            "api_key": self.AIRTABLE_API_KEY,
            "base_id": self.AIRTABLE_BASE_ID
        }
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration as a dictionary.
        
        Returns:
            dict: OpenAI configuration with api_key.
        """
        return {
            "api_key": self.OPENAI_API_KEY
        }
    
    def is_stop_word(self, word: str) -> bool:
        """Check if a word is a stop word that should be filtered out.
        
        Args:
            word: The word to check.
            
        Returns:
            bool: True if the word is a stop word, False otherwise.
        """
        return word.lower().strip() in self.STOP_WORDS
    
    def has_time_indicators(self, text: str) -> bool:
        """Check if text contains time-related keywords indicating a timed event.
        
        Args:
            text: The text to analyze.
            
        Returns:
            bool: True if text contains time indicators, False otherwise.
        """
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.TIME_INDICATORS)

