"""
MCP tools for document analysis and content processing.

This module provides AI assistants with tools to analyze school documents,
extract information, and provide summaries using AI-powered analysis.
"""

import logging
from typing import Dict, Any, Optional
from ..integrations.ai_analysis import AIAnalysis
from ..config.settings import Settings

logger = logging.getLogger(__name__)

class DocumentTools:
    """
    MCP tools for document analysis functionality.
    
    Provides AI assistants with document processing capabilities including:
    - Document summarization
    - Event extraction from announcements
    - Action item identification
    - Content analysis and categorization
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize document tools.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings
        openai_config = settings.get_openai_config()
        self.ai_analysis = AIAnalysis(api_key=openai_config["api_key"])
        logger.info("Initialized DocumentTools")
    
    async def analyze_document(self, text: str, analysis_type: str = "summary") -> str:
        """
        Analyze a document using AI-powered analysis.
        
        This tool provides comprehensive document analysis including:
        - Summarization of key points
        - Event extraction for calendar planning
        - Action item identification for task management
        
        Args:
            text: Document text to analyze
            analysis_type: Type of analysis ("summary", "events", "action_items")
            
        Returns:
            Formatted analysis results
        """
        try:
            logger.info(f"Analyzing document with type: {analysis_type}")
            
            # Validate analysis type
            valid_types = ["summary", "events", "action_items"]
            if analysis_type not in valid_types:
                return f"❌ Error: Invalid analysis_type '{analysis_type}'. Valid options: {', '.join(valid_types)}"
            
            # Validate text length
            if not text or len(text.strip()) < 10:
                return "❌ Error: Document text is too short for meaningful analysis."
            
            if len(text) > 10000:  # Reasonable limit for API calls
                text = text[:10000] + "... [truncated]"
                logger.warning("Document text truncated to 10,000 characters")
            
            # Perform analysis
            result = self.ai_analysis.analyze_document(text, analysis_type)
            
            if result.get("success"):
                return self._format_analysis_result(result, analysis_type)
            else:
                error_msg = result.get("error", "Unknown error occurred")
                return f"❌ Analysis failed: {error_msg}"
                
        except Exception as e:
            error_msg = f"❌ Error analyzing document: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def summarize_announcement(self, text: str) -> str:
        """
        Create a summary of a school announcement.
        
        This tool specifically analyzes school announcements to extract:
        - Brief summary of the content
        - Key points parents need to know
        - Important dates mentioned
        - Action items for parents/students
        
        Args:
            text: Announcement text to summarize
            
        Returns:
            Formatted summary with key information
        """
        try:
            logger.info("Summarizing school announcement")
            
            result = await self.analyze_document(text, "summary")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error summarizing announcement: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def extract_events(self, text: str) -> str:
        """
        Extract event information from a document.
        
        This tool analyzes documents to find events that parents and students
        need to know about, filtering out internal school operations and
        focusing on actionable events.
        
        Args:
            text: Document text to analyze for events
            
        Returns:
            Formatted list of extracted events
        """
        try:
            logger.info("Extracting events from document")
            
            result = await self.analyze_document(text, "events")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error extracting events: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def extract_action_items(self, text: str) -> str:
        """
        Extract action items and tasks from a document.
        
        This tool identifies specific tasks that parents or students need
        to complete, including deadlines and priority levels.
        
        Args:
            text: Document text to analyze for action items
            
        Returns:
            Formatted list of action items with deadlines and priorities
        """
        try:
            logger.info("Extracting action items from document")
            
            result = await self.analyze_document(text, "action_items")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error extracting action items: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _format_analysis_result(self, result: Dict[str, Any], analysis_type: str) -> str:
        """
        Format AI analysis results for display.
        
        Args:
            result: Analysis result from AI
            analysis_type: Type of analysis performed
            
        Returns:
            Formatted string for display
        """
        try:
            analysis_data = result.get("result", {})
            
            if analysis_type == "summary":
                return self._format_summary_result(analysis_data)
            elif analysis_type == "events":
                return self._format_events_result(analysis_data)
            elif analysis_type == "action_items":
                return self._format_action_items_result(analysis_data)
            else:
                return f"✅ Analysis completed: {str(analysis_data)}"
                
        except Exception as e:
            logger.error(f"Error formatting analysis result: {str(e)}")
            return f"✅ Analysis completed, but formatting failed: {str(result)}"
    
    def _format_summary_result(self, data: Dict[str, Any]) -> str:
        """Format summary analysis results."""
        try:
            result = "📄 **Document Summary**\\n\\n"
            
            # Main summary
            summary = data.get("summary", "No summary available")
            result += f"**Summary:** {summary}\\n\\n"
            
            # Key points
            key_points = data.get("key_points", [])
            if key_points:
                result += "**Key Points:**\\n"
                for i, point in enumerate(key_points, 1):
                    result += f"{i}. {point}\\n"
                result += "\\n"
            
            # Important dates
            important_dates = data.get("important_dates", [])
            if important_dates:
                result += "**Important Dates:**\\n"
                for date in important_dates:
                    result += f"📅 {date}\\n"
                result += "\\n"
            
            # Action items
            action_items = data.get("action_items", [])
            if action_items:
                result += "**Action Items:**\\n"
                for i, item in enumerate(action_items, 1):
                    result += f"{i}. {item}\\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error formatting summary: {str(e)}")
            return f"✅ Summary analysis completed: {str(data)}"
    
    def _format_events_result(self, data: Dict[str, Any]) -> str:
        """Format events analysis results."""
        try:
            events = data.get("events_found", [])
            total_events = data.get("total_events", len(events))
            
            if not events:
                return "📅 **Event Analysis**\\n\\nNo events found in the document."
            
            result = f"📅 **Event Analysis**\\n\\nFound {total_events} event(s):\\n\\n"
            
            for i, event in enumerate(events, 1):
                result += f"**Event {i}: {event.get('title', 'Unknown Event')}**\\n"
                result += f"📅 Date: {event.get('date', 'Unknown')}\\n"
                result += f"🕐 Time: {event.get('time', 'Unknown')}\\n"
                result += f"📍 Location: {event.get('location', 'Unknown')}\\n"
                result += f"📝 Description: {event.get('description', 'No description')}\\n"
                
                supplies = event.get('supplies_needed', 'None')
                if supplies and supplies != 'None':
                    result += f"🎒 Supplies Needed: {supplies}\\n"
                    
                    deadline = event.get('supplies_deadline', 'Unknown')
                    if deadline and deadline != 'Unknown':
                        result += f"⏰ Supplies Deadline: {deadline}\\n"
                
                result += "\\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error formatting events: {str(e)}")
            return f"✅ Event analysis completed: {str(data)}"
    
    def _format_action_items_result(self, data: Dict[str, Any]) -> str:
        """Format action items analysis results."""
        try:
            action_items = data.get("action_items", [])
            total_items = data.get("total_items", len(action_items))
            
            if not action_items:
                return "✅ **Action Items Analysis**\\n\\nNo action items found in the document."
            
            result = f"✅ **Action Items Analysis**\\n\\nFound {total_items} action item(s):\\n\\n"
            
            for i, item in enumerate(action_items, 1):
                priority = item.get('priority', 'medium')
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                
                result += f"**{i}. {item.get('task', 'Unknown task')}** {priority_emoji}\\n"
                result += f"👥 Who: {item.get('who', 'Unknown')}\\n"
                result += f"⏰ Deadline: {item.get('deadline', 'No deadline specified')}\\n"
                result += f"📊 Priority: {priority.title()}\\n\\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error formatting action items: {str(e)}")
            return f"✅ Action items analysis completed: {str(data)}"

