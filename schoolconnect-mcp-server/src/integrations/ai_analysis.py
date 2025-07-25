"""
AI analysis integration for document processing and content extraction.

This module provides AI-powered analysis capabilities for school documents,
announcements, and other text content using OpenAI's API.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIAnalysis:
    """
    AI-powered analysis client for document and content processing.
    
    Features:
    - Document summarization
    - Event extraction from announcements
    - Action item identification
    - Content analysis and categorization
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AI analysis client.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        logger.info("Initialized AI Analysis client")
    
    def analyze_document(self, text: str, analysis_type: str = "summary") -> Dict[str, Any]:
        """
        Analyze a document using AI.
        
        Args:
            text: Document text to analyze
            analysis_type: Type of analysis ('summary', 'events', 'action_items')
            
        Returns:
            Dict containing analysis results
        """
        try:
            if analysis_type == "summary":
                return self._summarize_document(text)
            elif analysis_type == "events":
                return self._extract_events(text)
            elif analysis_type == "action_items":
                return self._extract_action_items(text)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type
            }
    
    def _summarize_document(self, text: str) -> Dict[str, Any]:
        """
        Create a summary of the document.
        
        Args:
            text: Document text to summarize
            
        Returns:
            Dict containing summary and key points
        """
        try:
            prompt = f"""
            Please analyze this school announcement and provide:
            1. A brief summary (2-3 sentences)
            2. Key points (bullet list)
            3. Important dates mentioned
            4. Any action items for parents/students
            
            Announcement text:
            {text}
            
            Please format your response as JSON with the following structure:
            {{
                "summary": "Brief summary here",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "important_dates": ["Date 1", "Date 2"],
                "action_items": ["Action 1", "Action 2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that analyzes school announcements and documents. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content
            result_data = json.loads(result_text)
            
            return {
                "success": True,
                "analysis_type": "summary",
                "result": result_data
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            return {
                "success": False,
                "error": "Failed to parse AI response",
                "raw_response": response.choices[0].message.content if 'response' in locals() else None
            }
        except Exception as e:
            logger.error(f"Error in document summarization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_events(self, text: str) -> Dict[str, Any]:
        """
        Extract event information from the document.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Dict containing extracted event information
        """
        try:
            prompt = f"""
            Analyze this school announcement and extract any events or important dates.
            For each event found, provide:
            1. Event title/name
            2. Date (if mentioned)
            3. Time (if mentioned)
            4. Location (if mentioned)
            5. Description
            6. Any supplies needed
            7. Deadline for supplies (if mentioned)
            
            Only extract actual events that parents/students need to know about.
            Do NOT extract:
            - Regular classroom lessons
            - Internal assessments
            - Administrative tasks
            - General curriculum activities
            
            Announcement text:
            {text}
            
            Please format your response as JSON:
            {{
                "events_found": [
                    {{
                        "title": "Event name",
                        "date": "YYYY-MM-DD or 'Unknown'",
                        "time": "HH:MM or 'All day' or 'Unknown'",
                        "location": "Location or 'Unknown'",
                        "description": "Event description",
                        "supplies_needed": "List of supplies or 'None'",
                        "supplies_deadline": "YYYY-MM-DD or 'Unknown'"
                    }}
                ],
                "total_events": 0
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts event information from school announcements. Focus only on events relevant to parents and students. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content
            result_data = json.loads(result_text)
            
            return {
                "success": True,
                "analysis_type": "events",
                "result": result_data
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            return {
                "success": False,
                "error": "Failed to parse AI response",
                "raw_response": response.choices[0].message.content if 'response' in locals() else None
            }
        except Exception as e:
            logger.error(f"Error in event extraction: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_action_items(self, text: str) -> Dict[str, Any]:
        """
        Extract action items and tasks from the document.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Dict containing extracted action items
        """
        try:
            prompt = f"""
            Analyze this school announcement and extract any action items or tasks that parents/students need to do.
            
            For each action item, provide:
            1. What needs to be done
            2. Who needs to do it (parents, students, or both)
            3. Deadline (if mentioned)
            4. Priority level (high, medium, low)
            
            Examples of action items:
            - Submit permission slips
            - Bring supplies
            - Register for events
            - Complete forms
            - Make payments
            
            Announcement text:
            {text}
            
            Please format your response as JSON:
            {{
                "action_items": [
                    {{
                        "task": "Description of what needs to be done",
                        "who": "parents/students/both",
                        "deadline": "YYYY-MM-DD or 'No deadline specified'",
                        "priority": "high/medium/low"
                    }}
                ],
                "total_items": 0
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that identifies action items and tasks from school announcements. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content
            result_data = json.loads(result_text)
            
            return {
                "success": True,
                "analysis_type": "action_items",
                "result": result_data
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            return {
                "success": False,
                "error": "Failed to parse AI response",
                "raw_response": response.choices[0].message.content if 'response' in locals() else None
            }
        except Exception as e:
            logger.error(f"Error in action item extraction: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

