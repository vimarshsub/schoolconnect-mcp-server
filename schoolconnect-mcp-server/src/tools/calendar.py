"""
MCP tools for calendar event creation and management.

This module provides AI assistants with tools to create calendar events
and reminders in Google Calendar through n8n webhook integration.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..integrations.calendar_client import CalendarClient
from ..config.settings import Settings

logger = logging.getLogger(__name__)

class CalendarTools:
    """
    MCP tools for calendar functionality.
    
    Provides AI assistants with calendar event creation capabilities including:
    - All-day and timed event creation
    - Intelligent event type detection
    - Reminder creation with customizable timing
    - Event validation and formatting
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize calendar tools.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings
        self.calendar_client = CalendarClient(
            webhook_url=settings.N8N_WEBHOOK_URL,
            time_indicators=settings.TIME_INDICATORS
        )
        logger.info("Initialized CalendarTools")
    
    async def create_event(self, title: str, date: str, description: str = "",
                          location: str = "", event_type: str = "auto",
                          start_time: str = "09:00", duration_hours: int = 1) -> str:
        """
        Create a calendar event in Google Calendar.
        
        This tool creates calendar events with intelligent type detection:
        - Auto-detects whether event should be all-day or timed based on content
        - Supports both all-day events and timed events
        - Provides flexible scheduling options
        
        Args:
            title: Event title/name
            date: Event date in YYYY-MM-DD format
            description: Event description (optional)
            location: Event location (optional)
            event_type: Event type ("auto", "all_day", "timed")
            start_time: Start time for timed events in HH:MM format
            duration_hours: Duration in hours for timed events
            
        Returns:
            Success/failure message with event details
        """
        try:
            logger.info(f"Creating calendar event: {title} on {date}")
            
            # Validate date format
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return f"Error: Invalid date format '{date}'. Please use YYYY-MM-DD format."
            
            # Determine event type
            if event_type == "auto":
                all_day = None  # Let the client auto-detect
            elif event_type == "all_day":
                all_day = True
            elif event_type == "timed":
                all_day = False
            else:
                return f"Error: Invalid event_type '{event_type}'. Use 'auto', 'all_day', or 'timed'."
            
            # Validate start_time format for timed events
            if event_type == "timed" or (event_type == "auto" and not all_day):
                try:
                    datetime.strptime(start_time, '%H:%M')
                except ValueError:
                    return f"Error: Invalid start_time format '{start_time}'. Please use HH:MM format."
            
            # Create the event
            result = self.calendar_client.create_event(
                title=title,
                date=date,
                description=description,
                location=location,
                all_day=all_day,
                start_time=start_time,
                duration_hours=duration_hours
            )
            
            if result["success"]:
                event_type_str = result.get("event_type", "unknown")
                event_id = result.get("event_id", "unknown")
                
                success_msg = f"✅ Successfully created {event_type_str} calendar event: '{title}'\\n"
                success_msg += f"📅 Date: {date}\\n"
                
                if event_type_str == "timed":
                    end_time = (datetime.strptime(start_time, '%H:%M') + 
                              timedelta(hours=duration_hours)).strftime('%H:%M')
                    success_msg += f"🕐 Time: {start_time} - {end_time}\\n"
                
                if location:
                    success_msg += f"📍 Location: {location}\\n"
                
                if event_id and event_id != "unknown":
                    success_msg += f"🆔 Event ID: {event_id}\\n"
                
                success_msg += f"\\n📝 Description: {description}" if description else ""
                
                logger.info(f"Calendar event created successfully: {title}")
                return success_msg
            else:
                error_msg = f"❌ Failed to create calendar event: {result.get('message', 'Unknown error')}"
                logger.error(f"Calendar event creation failed: {title}")
                return error_msg
                
        except Exception as e:
            error_msg = f"❌ Error creating calendar event '{title}': {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def create_reminder(self, title: str, main_event_date: str, 
                            reminder_days_before: int = 3, description: str = "") -> str:
        """
        Create a reminder event before a main event.
        
        This tool creates reminder events to help parents remember important
        deadlines, supply requirements, or upcoming events.
        
        Args:
            title: Title of the main event (reminder will be prefixed with "REMINDER:")
            main_event_date: Date of the main event in YYYY-MM-DD format
            reminder_days_before: How many days before the event to set the reminder
            description: Additional description for the reminder
            
        Returns:
            Success/failure message with reminder details
        """
        try:
            logger.info(f"Creating reminder for: {title}, {reminder_days_before} days before {main_event_date}")
            
            # Validate main event date format
            try:
                main_date = datetime.strptime(main_event_date, '%Y-%m-%d')
            except ValueError:
                return f"Error: Invalid main_event_date format '{main_event_date}'. Please use YYYY-MM-DD format."
            
            # Calculate reminder date
            reminder_date = main_date - timedelta(days=reminder_days_before)
            reminder_date_str = reminder_date.strftime('%Y-%m-%d')
            
            # Check if reminder date is in the past
            if reminder_date < datetime.now():
                return f"⚠️ Warning: Reminder date {reminder_date_str} is in the past. The main event is too soon for a {reminder_days_before}-day reminder."
            
            # Create reminder description
            reminder_description = f"Reminder for upcoming event: {title}\\n"
            reminder_description += f"Main event date: {main_event_date}\\n"
            if description:
                reminder_description += f"\\nAdditional details: {description}"
            
            # Create the reminder event
            result = self.calendar_client.create_reminder(
                title=title,
                reminder_date=reminder_date_str,
                main_event_date=main_event_date,
                description=reminder_description
            )
            
            if result["success"]:
                event_id = result.get("event_id", "unknown")
                
                success_msg = f"🔔 Successfully created reminder for '{title}'\\n"
                success_msg += f"📅 Reminder Date: {reminder_date_str}\\n"
                success_msg += f"📅 Main Event Date: {main_event_date}\\n"
                success_msg += f"⏰ Days Before: {reminder_days_before}\\n"
                
                if event_id and event_id != "unknown":
                    success_msg += f"🆔 Reminder ID: {event_id}\\n"
                
                success_msg += f"\\n📝 Description: {reminder_description}"
                
                logger.info(f"Reminder created successfully for: {title}")
                return success_msg
            else:
                error_msg = f"❌ Failed to create reminder: {result.get('message', 'Unknown error')}"
                logger.error(f"Reminder creation failed for: {title}")
                return error_msg
                
        except Exception as e:
            error_msg = f"❌ Error creating reminder for '{title}': {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def create_event_with_reminder(self, title: str, event_date: str,
                                       description: str = "", location: str = "",
                                       event_type: str = "auto", start_time: str = "09:00",
                                       duration_hours: int = 1, 
                                       create_reminder_flag: bool = True,
                                       reminder_days_before: int = 3) -> str:
        """
        Create a calendar event and optionally create a reminder for it.
        
        This is a convenience tool that combines event creation with reminder creation
        for events that need advance notice.
        
        Args:
            title: Event title/name
            event_date: Event date in YYYY-MM-DD format
            description: Event description
            location: Event location
            event_type: Event type ("auto", "all_day", "timed")
            start_time: Start time for timed events
            duration_hours: Duration for timed events
            create_reminder_flag: Whether to create a reminder
            reminder_days_before: Days before event to set reminder
            
        Returns:
            Combined success/failure message for both event and reminder
        """
        try:
            logger.info(f"Creating event with reminder: {title} on {event_date}")
            
            # Create the main event
            event_result = await self.create_event(
                title=title,
                date=event_date,
                description=description,
                location=location,
                event_type=event_type,
                start_time=start_time,
                duration_hours=duration_hours
            )
            
            result_msg = event_result
            
            # Create reminder if requested
            if create_reminder_flag:
                reminder_result = await self.create_reminder(
                    title=title,
                    main_event_date=event_date,
                    reminder_days_before=reminder_days_before,
                    description=description
                )
                
                result_msg += f"\\n\\n{reminder_result}"
            
            return result_msg
            
        except Exception as e:
            error_msg = f"❌ Error creating event with reminder '{title}': {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _validate_date_format(self, date_str: str) -> bool:
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
    
    def _validate_time_format(self, time_str: str) -> bool:
        """
        Validate that a time string is in HH:MM format.
        
        Args:
            time_str: Time string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

