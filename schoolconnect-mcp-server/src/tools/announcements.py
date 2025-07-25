"""
MCP tools for school announcement access and search.

This module provides AI assistants with tools to search, filter, and retrieve
school announcements from Airtable with intelligent relevance ranking.
"""

import logging
from typing import List, Dict, Any, Optional
from ..integrations.airtable_client import AirtableClient
from ..config.settings import Settings

logger = logging.getLogger(__name__)

class AnnouncementTools:
    """
    MCP tools for announcement functionality.
    
    Provides AI assistants with comprehensive announcement access including:
    - Intelligent text search with relevance ranking
    - Date-based filtering with natural language support
    - Sender-based filtering
    - Recent announcements retrieval
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize announcement tools.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings
        airtable_config = settings.get_airtable_config()
        self.airtable_client = AirtableClient(
            api_key=airtable_config["api_key"],
            base_id=airtable_config["base_id"],
            stop_words=settings.STOP_WORDS
        )
        logger.info("Initialized AnnouncementTools")
    
    async def search_announcements(self, query: str, sender: Optional[str] = None,
                                 date_filter: Optional[str] = None, 
                                 limit: int = 15) -> str:
        """
        Search school announcements with intelligent relevance ranking.
        
        This tool provides comprehensive search functionality that:
        1. Filters out common stop words to prevent false matches
        2. Ranks results by relevance (exact matches score highest)
        3. Supports sender and date filtering
        4. Returns results in a user-friendly format
        
        Args:
            query: Search text to find in announcements
            sender: Optional sender name filter
            date_filter: Optional date filter (e.g., "in May", "last week")
            limit: Maximum number of results (default: 15)
            
        Returns:
            Formatted string with search results
        """
        try:
            logger.info(f"Searching announcements: query='{query}', sender='{sender}', date='{date_filter}'")
            
            # Validate limit
            if limit > self.settings.MAX_ANNOUNCEMENT_LIMIT:
                limit = self.settings.MAX_ANNOUNCEMENT_LIMIT
            
            # Perform combined search
            announcements = self.airtable_client.combined_filter_announcements(
                search_text=query,
                sender_name=sender,
                date_query=date_filter,
                limit=limit
            )
            
            if not announcements:
                return f"No announcements found matching '{query}'"
            
            # Format results
            result = self._format_announcement_results(announcements, query, limit)
            
            logger.info(f"Search completed: {len(announcements)} results returned")
            return result
            
        except Exception as e:
            error_msg = f"Error searching announcements: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def get_announcements_by_date(self, date_query: str, limit: int = 15) -> str:
        """
        Get announcements from a specific date range.
        
        Supports natural language date queries like:
        - "in May 2025"
        - "last week"
        - "today"
        - "yesterday"
        - "this month"
        
        Args:
            date_query: Natural language date query
            limit: Maximum number of results
            
        Returns:
            Formatted string with announcements from the date range
        """
        try:
            logger.info(f"Getting announcements by date: '{date_query}'")
            
            # Validate limit
            if limit > self.settings.MAX_ANNOUNCEMENT_LIMIT:
                limit = self.settings.MAX_ANNOUNCEMENT_LIMIT
            
            # Parse date and get announcements
            start_date, end_date = self.airtable_client.parse_natural_date(date_query)
            announcements = self.airtable_client.filter_by_date_range(start_date, end_date, limit)
            
            if not announcements:
                return f"No announcements found for '{date_query}' ({start_date} to {end_date})"
            
            # Format results with date context
            result = f"Found {len(announcements)} announcements from {date_query} ({start_date} to {end_date}):\\n\\n"
            result += self._format_announcement_list(announcements, limit)
            
            logger.info(f"Date query completed: {len(announcements)} results returned")
            return result
            
        except Exception as e:
            error_msg = f"Error getting announcements by date: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def get_recent_announcements(self, limit: int = 10) -> str:
        """
        Get the most recent school announcements.
        
        Args:
            limit: Number of recent announcements to retrieve
            
        Returns:
            Formatted string with recent announcements
        """
        try:
            logger.info(f"Getting {limit} recent announcements")
            
            # Validate limit
            if limit > self.settings.MAX_ANNOUNCEMENT_LIMIT:
                limit = self.settings.MAX_ANNOUNCEMENT_LIMIT
            
            # Get recent announcements
            announcements = self.airtable_client.get_all_announcements(limit=limit)
            
            if not announcements:
                return "No recent announcements found"
            
            # Format results
            result = f"Found {len(announcements)} recent announcements:\\n\\n"
            result += self._format_announcement_list(announcements, limit)
            
            logger.info(f"Recent announcements retrieved: {len(announcements)} results")
            return result
            
        except Exception as e:
            error_msg = f"Error getting recent announcements: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _format_announcement_results(self, announcements: List[Dict[str, Any]], 
                                   query: str, limit: int) -> str:
        """
        Format search results with context about the search.
        
        Args:
            announcements: List of announcement records
            query: Original search query
            limit: Requested limit
            
        Returns:
            Formatted string with search results and context
        """
        total_found = len(announcements)
        
        # Create header with search context
        result = f"Found {total_found} announcements matching '{query}':\\n\\n"
        
        # Add the formatted announcement list
        result += self._format_announcement_list(announcements, limit)
        
        # Add footer with additional context if results were limited
        if total_found >= limit:
            result += f"\\n\\nShowing first {limit} of {total_found} total results. "
            result += "Would you like to see more announcements or filter further?"
        
        return result
    
    def _format_announcement_list(self, announcements: List[Dict[str, Any]], 
                                limit: int) -> str:
        """
        Format a list of announcements for display.
        
        Args:
            announcements: List of announcement records
            limit: Maximum number to display
            
        Returns:
            Formatted string with numbered announcement list
        """
        if not announcements:
            return "No announcements to display."
        
        result_lines = []
        
        for i, announcement in enumerate(announcements[:limit], 1):
            fields = announcement.get('fields', {})
            
            # Extract key information
            title = fields.get('Title', 'No title')
            sent_by = fields.get('SentBy', 'Unknown sender')
            sent_time = fields.get('SentTime', 'Unknown date')
            description = fields.get('Description', 'No description')
            
            # Format sent time for display
            try:
                from datetime import datetime
                if sent_time and sent_time != 'Unknown date':
                    # Parse and reformat the date
                    dt = datetime.fromisoformat(sent_time.replace('Z', '+00:00'))
                    sent_time_formatted = dt.strftime('%B %d, %Y')
                else:
                    sent_time_formatted = sent_time
            except:
                sent_time_formatted = sent_time
            
            # Truncate description if too long
            if len(description) > 200:
                description = description[:200] + "..."
            
            # Format individual announcement
            announcement_text = f"{i}. **Title:** {title}\\n"
            announcement_text += f"   **Sent By:** {sent_by}\\n"
            announcement_text += f"   **Sent Time:** {sent_time_formatted}\\n"
            announcement_text += f"   **Description:** {description}\\n"
            
            result_lines.append(announcement_text)
        
        return "\\n".join(result_lines)
    
    def _extract_key_info(self, announcement: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract key information from an announcement record.
        
        Args:
            announcement: Announcement record from Airtable
            
        Returns:
            Dict with extracted key information
        """
        fields = announcement.get('fields', {})
        
        return {
            'title': fields.get('Title', 'No title'),
            'sent_by': fields.get('SentBy', 'Unknown sender'),
            'sent_time': fields.get('SentTime', 'Unknown date'),
            'description': fields.get('Description', 'No description'),
            'attachments': fields.get('Attachments', [])
        }

