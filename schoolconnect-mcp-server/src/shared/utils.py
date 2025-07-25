"""
Shared utility functions for SchoolConnect MCP Server.

This module provides common utility functions used across the MCP server,
including date handling, formatting, and validation utilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

def get_current_date() -> str:
    """
    Get the current date in YYYY-MM-DD format.
    
    Returns:
        Current date as string
    """
    return datetime.now().strftime('%Y-%m-%d')

def get_current_datetime() -> str:
    """
    Get the current datetime in ISO format.
    
    Returns:
        Current datetime as ISO string
    """
    return datetime.now().isoformat()

def format_date(date_obj: datetime) -> str:
    """
    Format a datetime object to YYYY-MM-DD string.
    
    Args:
        date_obj: Datetime object to format
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime('%Y-%m-%d')

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    try:
        return date_parser.parse(date_str)
    except Exception as e:
        logger.error(f"Failed to parse date '{date_str}': {str(e)}")
        return None

def validate_date_format(date_str: str) -> bool:
    """
    Validate that a date string is in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def calculate_date_range(days_back: int) -> Tuple[str, str]:
    """
    Calculate a date range going back a specified number of days.
    
    Args:
        days_back: Number of days to go back from today
        
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return (
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

def format_announcement_for_display(announcement: dict) -> str:
    """
    Format an announcement record for user-friendly display.
    
    Args:
        announcement: Announcement record from Airtable
        
    Returns:
        Formatted announcement string
    """
    fields = announcement.get('fields', {})
    
    title = fields.get('Title', 'No title')
    sent_by = fields.get('SentBy', 'Unknown sender')
    sent_time = fields.get('SentTime', 'Unknown date')
    description = fields.get('Description', 'No description')
    
    # Format sent time for display
    try:
        if sent_time and sent_time != 'Unknown date':
            dt = datetime.fromisoformat(sent_time.replace('Z', '+00:00'))
            sent_time_formatted = dt.strftime('%B %d, %Y at %I:%M %p')
        else:
            sent_time_formatted = sent_time
    except:
        sent_time_formatted = sent_time
    
    # Truncate description if too long
    if len(description) > 300:
        description = description[:300] + "..."
    
    return f"""**{title}**
📤 Sent by: {sent_by}
📅 Date: {sent_time_formatted}
📝 Description: {description}"""

def extract_event_description(announcement: dict) -> str:
    """
    Create a comprehensive event description from an announcement.
    
    Args:
        announcement: Announcement record from Airtable
        
    Returns:
        Formatted event description
    """
    fields = announcement.get('fields', {})
    
    description_parts = []
    
    # Add main description
    main_desc = fields.get('Description', '')
    if main_desc:
        description_parts.append(f"Event extracted from SchoolConnect announcement")
        description_parts.append(f"")
        description_parts.append(f"Announcement: {fields.get('Title', 'No title')}")
        description_parts.append(f"")
        description_parts.append(main_desc)
    
    # Add extraction timestamp
    description_parts.append(f"")
    description_parts.append(f"Extracted on: {get_current_datetime()}")
    
    return "\\n".join(description_parts)

def clean_text_for_search(text: str) -> str:
    """
    Clean and normalize text for search operations.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase and strip whitespace
    cleaned = text.lower().strip()
    
    # Remove extra whitespace
    import re
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned

def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def safe_get_field(record: dict, field_name: str, default: str = "") -> str:
    """
    Safely get a field value from an Airtable record.
    
    Args:
        record: Airtable record
        field_name: Name of the field to get
        default: Default value if field is missing
        
    Returns:
        Field value or default
    """
    return record.get('fields', {}).get(field_name, default)

