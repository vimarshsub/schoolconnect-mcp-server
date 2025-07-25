#!/usr/bin/env python3
"""
SchoolConnect MCP Server

This server provides AI assistants with tools to access school announcements,
create calendar events, and analyze documents through the Model Context Protocol (MCP).

Features:
- Intelligent announcement search with relevance ranking
- Calendar event creation with all-day/timed event support
- AI-powered document analysis and summarization
- Natural language date filtering
- Comprehensive error handling and logging

Usage:
    python server.py

Environment Variables Required:
    AIRTABLE_API_KEY - Your Airtable API key
    AIRTABLE_BASE_ID - Your Airtable base ID
    OPENAI_API_KEY - Your OpenAI API key
    N8N_WEBHOOK_URL - Your n8n webhook URL for calendar integration
"""

import asyncio
import logging
import sys
from typing import Any, Sequence

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Local imports
from src.config.settings import Settings
from src.tools.announcements import AnnouncementTools
from src.tools.calendar import CalendarTools
from src.tools.documents import DocumentTools

# Initialize settings and logging
settings = Settings()
settings.setup_logging()
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("schoolconnect-mcp-server")

# Initialize tool classes
announcement_tools = None
calendar_tools = None
document_tools = None

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List all available MCP tools.
    
    Returns:
        List of available tools with their descriptions and parameters
    """
    return [
        # Announcement Tools
        Tool(
            name="search_announcements",
            description="Search school announcements with intelligent relevance ranking. Supports text search, sender filtering, and date filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search text to find in announcements (e.g., 'field trip', 'lemonade sale')"
                    },
                    "sender": {
                        "type": "string",
                        "description": "Optional: Filter by sender name (e.g., 'Jessica Arciniega')"
                    },
                    "date_filter": {
                        "type": "string", 
                        "description": "Optional: Date filter using natural language (e.g., 'in May', 'last week', 'today')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 15, max: 50)",
                        "default": 15
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_announcements_by_date",
            description="Get announcements from a specific date range using natural language queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_query": {
                        "type": "string",
                        "description": "Natural language date query (e.g., 'in May 2025', 'last week', 'today', 'yesterday')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 15)",
                        "default": 15
                    }
                },
                "required": ["date_query"]
            }
        ),
        Tool(
            name="get_recent_announcements",
            description="Get the most recent school announcements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent announcements to retrieve (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        
        # Calendar Tools
        Tool(
            name="create_calendar_event",
            description="Create a calendar event in Google Calendar. Automatically detects whether event should be all-day or timed based on content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Event title/name"
                    },
                    "date": {
                        "type": "string",
                        "description": "Event date in YYYY-MM-DD format"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description (optional)",
                        "default": ""
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location (optional)",
                        "default": ""
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Event type: 'auto' (detect automatically), 'all_day', or 'timed'",
                        "enum": ["auto", "all_day", "timed"],
                        "default": "auto"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time for timed events in HH:MM format (default: 09:00)",
                        "default": "09:00"
                    },
                    "duration_hours": {
                        "type": "integer",
                        "description": "Duration in hours for timed events (default: 1)",
                        "default": 1
                    }
                },
                "required": ["title", "date"]
            }
        ),
        Tool(
            name="create_reminder",
            description="Create a reminder event before a main event to help remember important deadlines or preparations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the main event (reminder will be prefixed with 'REMINDER:')"
                    },
                    "main_event_date": {
                        "type": "string",
                        "description": "Date of the main event in YYYY-MM-DD format"
                    },
                    "reminder_days_before": {
                        "type": "integer",
                        "description": "How many days before the event to set the reminder (default: 3)",
                        "default": 3
                    },
                    "description": {
                        "type": "string",
                        "description": "Additional description for the reminder (optional)",
                        "default": ""
                    }
                },
                "required": ["title", "main_event_date"]
            }
        ),
        Tool(
            name="create_event_with_reminder",
            description="Create a calendar event and optionally create a reminder for it. Convenience tool for events that need advance notice.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Event title/name"
                    },
                    "event_date": {
                        "type": "string",
                        "description": "Event date in YYYY-MM-DD format"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description",
                        "default": ""
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location",
                        "default": ""
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Event type: 'auto', 'all_day', or 'timed'",
                        "enum": ["auto", "all_day", "timed"],
                        "default": "auto"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time for timed events (HH:MM)",
                        "default": "09:00"
                    },
                    "duration_hours": {
                        "type": "integer",
                        "description": "Duration for timed events",
                        "default": 1
                    },
                    "create_reminder_flag": {
                        "type": "boolean",
                        "description": "Whether to create a reminder",
                        "default": True
                    },
                    "reminder_days_before": {
                        "type": "integer",
                        "description": "Days before event to set reminder",
                        "default": 3
                    }
                },
                "required": ["title", "event_date"]
            }
        ),
        
        # Document Analysis Tools
        Tool(
            name="analyze_document",
            description="Analyze a document using AI-powered analysis. Supports summarization, event extraction, and action item identification.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Document text to analyze"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis to perform",
                        "enum": ["summary", "events", "action_items"],
                        "default": "summary"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="summarize_announcement",
            description="Create a summary of a school announcement with key points, dates, and action items.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Announcement text to summarize"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="extract_events",
            description="Extract event information from a document, focusing on events relevant to parents and students.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Document text to analyze for events"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="extract_action_items",
            description="Extract action items and tasks from a document with deadlines and priority levels.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Document text to analyze for action items"
                    }
                },
                "required": ["text"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.
    
    Args:
        name: Name of the tool to call
        arguments: Arguments for the tool
        
    Returns:
        List of text content with tool results
    """
    try:
        logger.info(f"Tool called: {name} with arguments: {arguments}")
        
        # Announcement tools
        if name == "search_announcements":
            result = await announcement_tools.search_announcements(
                query=arguments["query"],
                sender=arguments.get("sender"),
                date_filter=arguments.get("date_filter"),
                limit=arguments.get("limit", 15)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_announcements_by_date":
            result = await announcement_tools.get_announcements_by_date(
                date_query=arguments["date_query"],
                limit=arguments.get("limit", 15)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_recent_announcements":
            result = await announcement_tools.get_recent_announcements(
                limit=arguments.get("limit", 10)
            )
            return [TextContent(type="text", text=result)]
        
        # Calendar tools
        elif name == "create_calendar_event":
            result = await calendar_tools.create_event(
                title=arguments["title"],
                date=arguments["date"],
                description=arguments.get("description", ""),
                location=arguments.get("location", ""),
                event_type=arguments.get("event_type", "auto"),
                start_time=arguments.get("start_time", "09:00"),
                duration_hours=arguments.get("duration_hours", 1)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "create_reminder":
            result = await calendar_tools.create_reminder(
                title=arguments["title"],
                main_event_date=arguments["main_event_date"],
                reminder_days_before=arguments.get("reminder_days_before", 3),
                description=arguments.get("description", "")
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "create_event_with_reminder":
            result = await calendar_tools.create_event_with_reminder(
                title=arguments["title"],
                event_date=arguments["event_date"],
                description=arguments.get("description", ""),
                location=arguments.get("location", ""),
                event_type=arguments.get("event_type", "auto"),
                start_time=arguments.get("start_time", "09:00"),
                duration_hours=arguments.get("duration_hours", 1),
                create_reminder_flag=arguments.get("create_reminder_flag", True),
                reminder_days_before=arguments.get("reminder_days_before", 3)
            )
            return [TextContent(type="text", text=result)]
        
        # Document analysis tools
        elif name == "analyze_document":
            result = await document_tools.analyze_document(
                text=arguments["text"],
                analysis_type=arguments.get("analysis_type", "summary")
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "summarize_announcement":
            result = await document_tools.summarize_announcement(
                text=arguments["text"]
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "extract_events":
            result = await document_tools.extract_events(
                text=arguments["text"]
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "extract_action_items":
            result = await document_tools.extract_action_items(
                text=arguments["text"]
            )
            return [TextContent(type="text", text=result)]
        
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
            
    except Exception as e:
        error_msg = f"Error executing tool '{name}': {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

async def main():
    """
    Main entry point for the MCP server.
    """
    global announcement_tools, calendar_tools, document_tools
    
    try:
        # Validate configuration
        settings.validate()
        logger.info("Configuration validated successfully")
        
        # Initialize tool classes
        announcement_tools = AnnouncementTools(settings)
        calendar_tools = CalendarTools(settings)
        document_tools = DocumentTools(settings)
        
        logger.info("SchoolConnect MCP Server initialized successfully")
        logger.info("Available tools: announcements, calendar, documents")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="schoolconnect-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )
            
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the server
    asyncio.run(main())

