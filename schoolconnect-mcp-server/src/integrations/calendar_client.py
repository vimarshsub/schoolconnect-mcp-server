"""
Calendar integration client for creating events via n8n webhooks.

This module handles the creation of calendar events and reminders in Google Calendar
through n8n webhook automation, supporting both all-day and timed events.
"""

import logging
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class CalendarClient:
    """
    Client for creating calendar events through n8n webhooks.
    
    Features:
    - All-day and timed event creation
    - Intelligent event type detection
    - Reminder event creation
    - Hybrid data format for backward compatibility
    """
    
    def __init__(self, webhook_url: str, time_indicators: set):
        """
        Initialize the calendar client.
        
        Args:
            webhook_url: n8n webhook URL for calendar integration
            time_indicators: Set of words that indicate timed events
        """
        self.webhook_url = webhook_url
        self.time_indicators = time_indicators
        logger.info("Initialized Calendar client")
    
    def detect_event_type(self, title: str, description: str = "") -> bool:
        """
        Detect whether an event should be all-day or timed based on content.
        
        This method analyzes the event title and description for time-related keywords
        to determine if it should be created as a timed event or all-day event.
        
        Args:
            title: Event title
            description: Event description
            
        Returns:
            bool: True if should be all-day event, False if should be timed event
        """
        combined_text = f"{title} {description}".lower()
        
        # Check for specific time patterns (e.g., "9:00 AM", "2:30 PM")
        time_pattern = r'\b\d{1,2}:\d{2}\s*(am|pm|a\.m\.|p\.m\.)\b'
        if re.search(time_pattern, combined_text):
            logger.debug(f"Found specific time pattern in: {title}")
            return False  # Timed event
        
        # Check for time indicator words
        for indicator in self.time_indicators:
            if indicator in combined_text:
                logger.debug(f"Found time indicator '{indicator}' in: {title}")
                return False  # Timed event
        
        # Default to all-day event
        logger.debug(f"No time indicators found, creating all-day event: {title}")
        return True  # All-day event
    
    def format_event_data(self, title: str, date: str, description: str = "", 
                         location: str = "", all_day: Optional[bool] = None,
                         start_time: str = "09:00", duration_hours: int = 1) -> Dict[str, Any]:
        """
        Format event data for n8n webhook with hybrid datetime/date support.
        
        This method creates a data structure that supports both all-day and timed events,
        sending both date and datetime formats for maximum compatibility.
        
        Args:
            title: Event title
            date: Event date in YYYY-MM-DD format
            description: Event description
            location: Event location
            all_day: Force all-day (True) or timed (False), None for auto-detection
            start_time: Start time for timed events (HH:MM format)
            duration_hours: Duration in hours for timed events
            
        Returns:
            Dict containing formatted event data for n8n webhook
        """
        try:
            # Parse the date
            event_date = datetime.strptime(date, '%Y-%m-%d')
            
            # Determine event type
            if all_day is None:
                is_all_day = self.detect_event_type(title, description)
            else:
                is_all_day = all_day
            
            # Create base event data
            event_data = {
                "action": "create_event",
                "title": title,
                "description": description,
                "location": location,
                "all_day": is_all_day
            }
            
            if is_all_day:
                # All-day event: use date format
                event_data.update({
                    "start_date": event_date.strftime('%Y-%m-%d'),
                    "end_date": (event_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    # Also include datetime format for backward compatibility
                    "start_datetime": event_date.strftime('%Y-%m-%dT00:00:00'),
                    "end_datetime": (event_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
                })
                logger.debug(f"Formatted all-day event: {title} on {date}")
            else:
                # Timed event: use datetime format
                start_datetime = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
                end_datetime = start_datetime + timedelta(hours=duration_hours)
                
                event_data.update({
                    "start_datetime": start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                    "end_datetime": end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                    # Also include date format for compatibility
                    "start_date": event_date.strftime('%Y-%m-%d'),
                    "end_date": event_date.strftime('%Y-%m-%d')
                })
                logger.debug(f"Formatted timed event: {title} from {start_datetime} to {end_datetime}")
            
            return event_data
            
        except Exception as e:
            logger.error(f"Error formatting event data: {str(e)}")
            raise
    
    def create_event(self, title: str, date: str, description: str = "",
                    location: str = "", all_day: Optional[bool] = None,
                    start_time: str = "09:00", duration_hours: int = 1) -> Dict[str, Any]:
        """
        Create a calendar event via n8n webhook.
        
        Args:
            title: Event title
            date: Event date in YYYY-MM-DD format
            description: Event description
            location: Event location
            all_day: Force all-day (True) or timed (False), None for auto-detection
            start_time: Start time for timed events (HH:MM format)
            duration_hours: Duration in hours for timed events
            
        Returns:
            Dict containing success status and any returned event information
        """
        try:
            if not self.webhook_url:
                raise ValueError("No webhook URL configured for calendar integration")
            
            # Format event data
            event_data = self.format_event_data(
                title=title,
                date=date,
                description=description,
                location=location,
                all_day=all_day,
                start_time=start_time,
                duration_hours=duration_hours
            )
            
            logger.info(f"Creating calendar event: {title} on {date}")
            
            # Send to n8n webhook
            response = requests.post(
                self.webhook_url,
                json=event_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response.raise_for_status()
            
            # Try to parse response
            try:
                response_data = response.json()
            except:
                response_data = {"message": response.text}
            
            # Extract event ID if available
            event_id = self._extract_event_id(response_data)
            
            result = {
                "success": True,
                "message": f"Successfully created calendar event: {title}",
                "event_id": event_id,
                "event_type": "all-day" if event_data["all_day"] else "timed",
                "webhook_response": response_data
            }
            
            logger.info(f"Calendar event created successfully: {title} (ID: {event_id})")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create calendar event '{title}': {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "event_id": None
            }
        except Exception as e:
            error_msg = f"Error creating calendar event '{title}': {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "event_id": None
            }
    
    def create_reminder(self, title: str, reminder_date: str, main_event_date: str,
                       description: str) -> Dict[str, Any]:
        """
        Create a reminder event before a main event.
        
        Args:
            title: Reminder title
            reminder_date: Date for the reminder (YYYY-MM-DD format)
            main_event_date: Date of the main event
            description: Reminder description
            
        Returns:
            Dict containing success status and event information
        """
        try:
            # Format reminder title
            reminder_title = f"REMINDER: {title}"
            
            # Create reminder description
            reminder_description = f"{description}\n\nMain event date: {main_event_date}"
            
            logger.info(f"Creating reminder: {reminder_title} on {reminder_date}")
            
            # Create reminder as all-day event
            result = self.create_event(
                title=reminder_title,
                date=reminder_date,
                description=reminder_description,
                all_day=True  # Reminders are always all-day
            )
            
            if result["success"]:
                result["message"] = f"Successfully created reminder: {title}"
                logger.info(f"Reminder created successfully: {title}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error creating reminder '{title}': {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "event_id": None
            }
    
    def _extract_event_id(self, response_data: Any) -> Optional[str]:
        """
        Extract event ID from n8n webhook response.
        
        This method attempts to find the Google Calendar event ID in various
        possible response formats from the n8n webhook.
        
        Args:
            response_data: Response data from n8n webhook
            
        Returns:
            Event ID if found, None otherwise
        """
        if not response_data:
            return None
        
        # If response is a string, try to extract ID from it
        if isinstance(response_data, str):
            # Look for patterns like "event ID: abc123" or "id: abc123"
            id_patterns = [
                r'event\s+id[:\s]+([a-zA-Z0-9_-]+)',
                r'id[:\s]+([a-zA-Z0-9_-]+)',
                r'created\s+event[:\s]+([a-zA-Z0-9_-]+)'
            ]
            
            for pattern in id_patterns:
                match = re.search(pattern, response_data, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        
        # If response is a dict, look for common ID field names
        if isinstance(response_data, dict):
            id_fields = ['id', 'event_id', 'eventId', 'calendar_event_id', 'google_event_id']
            
            for field in id_fields:
                if field in response_data and response_data[field]:
                    return str(response_data[field])
            
            # Look in nested objects
            for key, value in response_data.items():
                if isinstance(value, dict):
                    for id_field in id_fields:
                        if id_field in value and value[id_field]:
                            return str(value[id_field])
        
        return None

