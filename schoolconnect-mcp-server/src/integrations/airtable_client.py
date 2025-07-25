"""
Airtable integration client with intelligent search capabilities.

This module provides comprehensive access to school announcements stored in Airtable,
including advanced search functionality with relevance ranking.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from airtable import Airtable
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class AirtableClient:
    """
    Client for interacting with Airtable announcements database.
    
    Features:
    - Intelligent search with relevance scoring
    - Stop words filtering to prevent false matches
    - Date range filtering with natural language support
    - Sender-based filtering
    - Comprehensive announcement retrieval
    """
    
    def __init__(self, api_key: str, base_id: str, stop_words: set):
        """
        Initialize the Airtable client.
        
        Args:
            api_key: Airtable API key
            base_id: Airtable base ID
            stop_words: Set of words to filter out during search
        """
        self.airtable = Airtable(base_id, 'Announcements', api_key)
        self.stop_words = stop_words
        logger.info(f"Initialized Airtable client for base: {base_id}")
    
    def get_all_announcements(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all announcements from Airtable.
        
        Args:
            limit: Maximum number of announcements to retrieve
            
        Returns:
            List of announcement records
        """
        try:
            logger.info(f"Fetching all announcements (limit: {limit})")
            
            # Get all records
            all_records = self.airtable.get_all()
            
            # Sort by SentTime (most recent first)
            sorted_records = sorted(
                all_records,
                key=lambda x: x['fields'].get('SentTime', ''),
                reverse=True
            )
            
            # Apply limit if specified
            if limit:
                sorted_records = sorted_records[:limit]
            
            logger.info(f"Retrieved {len(sorted_records)} announcements")
            return sorted_records
            
        except Exception as e:
            logger.error(f"Error fetching announcements: {str(e)}")
            return []
    
    def filter_by_date_range(self, start_date: str, end_date: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Filter announcements by date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of results
            
        Returns:
            List of filtered announcement records
        """
        try:
            # Create Airtable formula for date filtering
            formula = f"AND(IS_AFTER({{SentTime}}, '{start_date}T00:00:00.000Z'), IS_BEFORE({{SentTime}}, '{end_date}T23:59:59.000Z'))"
            
            logger.info(f"Filtering announcements from {start_date} to {end_date}")
            
            # Get filtered records
            records = self.airtable.get_all(formula=formula)
            
            # Sort by SentTime (most recent first)
            sorted_records = sorted(
                records,
                key=lambda x: x['fields'].get('SentTime', ''),
                reverse=True
            )
            
            # Apply limit if specified
            if limit:
                sorted_records = sorted_records[:limit]
            
            logger.info(f"Found {len(sorted_records)} announcements in date range")
            return sorted_records
            
        except Exception as e:
            logger.error(f"Error filtering by date range: {str(e)}")
            return []
    
    def parse_natural_date(self, date_query: str) -> Tuple[str, str]:
        """
        Parse natural language date queries into start and end dates.
        
        Args:
            date_query: Natural language date query (e.g., "in May", "last week", "today")
            
        Returns:
            Tuple of (start_date, end_date) in YYYY-MM-DD format
        """
        today = datetime.now()
        date_query_lower = date_query.lower().strip()
        
        try:
            # Handle "today"
            if 'today' in date_query_lower:
                date_str = today.strftime('%Y-%m-%d')
                return date_str, date_str
            
            # Handle "yesterday"
            if 'yesterday' in date_query_lower:
                yesterday = today - timedelta(days=1)
                date_str = yesterday.strftime('%Y-%m-%d')
                return date_str, date_str
            
            # Handle "this week"
            if 'this week' in date_query_lower:
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')
            
            # Handle "last week"
            if 'last week' in date_query_lower:
                start_of_last_week = today - timedelta(days=today.weekday() + 7)
                end_of_last_week = start_of_last_week + timedelta(days=6)
                return start_of_last_week.strftime('%Y-%m-%d'), end_of_last_week.strftime('%Y-%m-%d')
            
            # Handle month names (e.g., "in May", "May 2025")
            month_patterns = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12,
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            for month_name, month_num in month_patterns.items():
                if month_name in date_query_lower:
                    # Extract year if present, otherwise use current year
                    year_match = re.search(r'20\d{2}', date_query)
                    year = int(year_match.group()) if year_match else today.year
                    
                    # Create start and end of month
                    start_date = datetime(year, month_num, 1)
                    if month_num == 12:
                        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
                    
                    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            
            # Handle "last X days"
            days_match = re.search(r'last (\d+) days?', date_query_lower)
            if days_match:
                days = int(days_match.group(1))
                start_date = today - timedelta(days=days)
                return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
            
            # Try to parse as a specific date
            try:
                parsed_date = date_parser.parse(date_query)
                date_str = parsed_date.strftime('%Y-%m-%d')
                return date_str, date_str
            except:
                pass
            
            # Default: last 30 days
            logger.warning(f"Could not parse date query '{date_query}', defaulting to last 30 days")
            start_date = today - timedelta(days=30)
            return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.error(f"Error parsing date query '{date_query}': {str(e)}")
            # Default fallback
            start_date = today - timedelta(days=30)
            return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    
    def filter_stop_words(self, keywords: List[str]) -> List[str]:
        """
        Filter out stop words from a list of keywords.
        
        Args:
            keywords: List of keywords to filter
            
        Returns:
            List of keywords with stop words removed
        """
        filtered = [word for word in keywords if not self._is_stop_word(word)]
        logger.debug(f"Filtered keywords: {keywords} -> {filtered}")
        return filtered
    
    def _is_stop_word(self, word: str) -> bool:
        """Check if a word is a stop word."""
        return word.lower().strip() in self.stop_words
    
    def calculate_relevance_score(self, announcement: Dict[str, Any], search_text: str, keywords: List[str]) -> int:
        """
        Calculate relevance score for an announcement based on search criteria.
        
        Scoring system:
        - Exact phrase match: 100 points (highest priority)
        - Clean phrase match (no stop words): 80 points  
        - Multiple keyword match: 60+ points (bonus for additional keywords)
        - Single keyword match: 20 points (lowest priority)
        - Title matches get bonus points
        
        Args:
            announcement: Announcement record from Airtable
            search_text: Original search text
            keywords: List of search keywords
            
        Returns:
            Relevance score (higher = more relevant)
        """
        fields = announcement.get('fields', {})
        title = fields.get('Title', '').lower()
        description = fields.get('Description', '').lower()
        sender = fields.get('SentBy', '').lower()
        
        # Combine all searchable text
        searchable_text = f"{title} {description} {sender}"
        search_lower = search_text.lower()
        
        score = 0
        
        # 1. Exact phrase match (highest priority)
        if search_lower in searchable_text:
            score += 100
            if search_lower in title:  # Bonus for title match
                score += 20
            logger.debug(f"Exact phrase match found: +{score} points")
            return score
        
        # 2. Clean phrase match (search text without stop words)
        clean_search_words = self.filter_stop_words(search_text.split())
        clean_search_phrase = ' '.join(clean_search_words).lower()
        
        if clean_search_phrase and clean_search_phrase in searchable_text:
            score += 80
            if clean_search_phrase in title:  # Bonus for title match
                score += 15
            logger.debug(f"Clean phrase match found: +{score} points")
            return score
        
        # 3. Multiple keyword matching
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in searchable_text:
                matched_keywords.append(keyword)
                score += 20  # Base score for each keyword
                
                # Bonus points for title matches
                if keyword.lower() in title:
                    score += 10
        
        # Bonus for multiple keyword matches
        if len(matched_keywords) > 1:
            score += (len(matched_keywords) - 1) * 10
        
        logger.debug(f"Keyword matches: {matched_keywords}, score: {score}")
        return score
    
    def search_announcements(self, search_text: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search announcements with intelligent relevance ranking.
        
        This method implements a sophisticated search algorithm that:
        1. Filters out common stop words to prevent false matches
        2. Scores results based on relevance (exact matches, phrase matches, keyword matches)
        3. Prioritizes title matches over description matches
        4. Returns results sorted by relevance score
        
        Args:
            search_text: Text to search for in announcements
            limit: Maximum number of results to return
            
        Returns:
            List of announcement records sorted by relevance (most relevant first)
        """
        try:
            logger.info(f"Searching announcements for: '{search_text}'")
            
            # Get all announcements
            all_announcements = self.get_all_announcements()
            
            if not all_announcements:
                logger.warning("No announcements found in database")
                return []
            
            # Prepare search keywords (filter stop words)
            keywords = [word.strip() for word in search_text.split() if word.strip()]
            filtered_keywords = self.filter_stop_words(keywords)
            
            logger.info(f"Search keywords (filtered): {filtered_keywords}")
            
            # Score and filter announcements
            scored_announcements = []
            
            for announcement in all_announcements:
                score = self.calculate_relevance_score(announcement, search_text, filtered_keywords)
                
                # Only include announcements with a positive score
                if score > 0:
                    scored_announcements.append({
                        'announcement': announcement,
                        'score': score
                    })
            
            # Sort by score (highest first)
            scored_announcements.sort(key=lambda x: x['score'], reverse=True)
            
            # Extract just the announcements
            results = [item['announcement'] for item in scored_announcements]
            
            # Apply limit if specified
            if limit:
                results = results[:limit]
            
            logger.info(f"Found {len(results)} relevant announcements")
            
            # Log top results for debugging
            for i, item in enumerate(scored_announcements[:5]):
                title = item['announcement']['fields'].get('Title', 'No title')
                logger.debug(f"Result {i+1}: '{title}' (score: {item['score']})")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching announcements: {str(e)}")
            return []
    
    def combined_filter_announcements(self, search_text: Optional[str] = None, 
                                    sender_name: Optional[str] = None,
                                    date_query: Optional[str] = None,
                                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Advanced filtering combining text search, sender filtering, and date filtering.
        
        This is the main search method that combines all filtering capabilities:
        1. Date filtering (if date_query provided)
        2. Sender filtering (if sender_name provided)  
        3. Text search with relevance ranking (if search_text provided)
        
        Args:
            search_text: Text to search for in announcements
            sender_name: Filter by sender name
            date_query: Natural language date query
            limit: Maximum number of results
            
        Returns:
            List of filtered and ranked announcement records
        """
        try:
            logger.info(f"Combined filter - search: '{search_text}', sender: '{sender_name}', date: '{date_query}'")
            
            # Start with all announcements or date-filtered announcements
            if date_query:
                start_date, end_date = self.parse_natural_date(date_query)
                announcements = self.filter_by_date_range(start_date, end_date)
                logger.info(f"Date filtering: {len(announcements)} announcements from {start_date} to {end_date}")
            else:
                announcements = self.get_all_announcements()
            
            # Filter by sender if specified
            if sender_name:
                sender_lower = sender_name.lower()
                announcements = [
                    ann for ann in announcements
                    if sender_lower in ann['fields'].get('SentBy', '').lower()
                ]
                logger.info(f"Sender filtering: {len(announcements)} announcements from '{sender_name}'")
            
            # Apply text search if specified
            if search_text:
                # Score and rank the filtered announcements
                scored_announcements = []
                keywords = [word.strip() for word in search_text.split() if word.strip()]
                filtered_keywords = self.filter_stop_words(keywords)
                
                for announcement in announcements:
                    score = self.calculate_relevance_score(announcement, search_text, filtered_keywords)
                    if score > 0:
                        scored_announcements.append({
                            'announcement': announcement,
                            'score': score
                        })
                
                # Sort by relevance score
                scored_announcements.sort(key=lambda x: x['score'], reverse=True)
                announcements = [item['announcement'] for item in scored_announcements]
                
                logger.info(f"Text search: {len(announcements)} relevant announcements")
            
            # Apply limit
            if limit:
                announcements = announcements[:limit]
            
            logger.info(f"Final result: {len(announcements)} announcements")
            return announcements
            
        except Exception as e:
            logger.error(f"Error in combined filter: {str(e)}")
            return []

