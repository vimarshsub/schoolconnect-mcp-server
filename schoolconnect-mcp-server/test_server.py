#!/usr/bin/env python3
"""
Test script for SchoolConnect MCP Server

This script validates the server configuration and basic functionality
without requiring actual MCP client connections.
"""

import os
import sys
import asyncio
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import Settings
from src.tools.announcements import AnnouncementTools
from src.tools.calendar import CalendarTools
from src.tools.documents import DocumentTools

async def test_configuration():
    """Test configuration loading and validation."""
    print("🔧 Testing configuration...")
    
    try:
        # Test with mock environment variables
        with patch.dict(os.environ, {
            'AIRTABLE_API_KEY': 'test_key',
            'AIRTABLE_BASE_ID': 'test_base',
            'OPENAI_API_KEY': 'test_openai_key',
            'N8N_WEBHOOK_URL': 'https://test.webhook.url'
        }):
            settings = Settings()
            settings.validate()
            print("✅ Configuration validation passed")
            return settings
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return None

async def test_tool_initialization(settings):
    """Test tool class initialization."""
    print("🛠️ Testing tool initialization...")
    
    try:
        announcement_tools = AnnouncementTools(settings)
        calendar_tools = CalendarTools(settings)
        document_tools = DocumentTools(settings)
        
        print("✅ All tool classes initialized successfully")
        return announcement_tools, calendar_tools, document_tools
    except Exception as e:
        print(f"❌ Tool initialization failed: {e}")
        return None, None, None

async def test_announcement_tools(announcement_tools):
    """Test announcement tools with mock data."""
    print("📢 Testing announcement tools...")
    
    try:
        # Mock the Airtable client to avoid actual API calls
        with patch.object(announcement_tools.airtable_client, 'search_announcements') as mock_search:
            mock_search.return_value = {
                'success': True,
                'announcements': [
                    {
                        'id': 'test1',
                        'fields': {
                            'Title': 'Test Announcement',
                            'SentBy': 'Test Sender',
                            'SentTime': '2025-01-15T10:00:00.000Z',
                            'Description': 'This is a test announcement'
                        }
                    }
                ],
                'total_count': 1
            }
            
            result = await announcement_tools.search_announcements("test")
            if "Test Announcement" in result:
                print("✅ Announcement search test passed")
            else:
                print("❌ Announcement search test failed")
                
    except Exception as e:
        print(f"❌ Announcement tools test failed: {e}")

async def test_calendar_tools(calendar_tools):
    """Test calendar tools with mock data."""
    print("📅 Testing calendar tools...")
    
    try:
        # Mock the calendar client to avoid actual webhook calls
        with patch.object(calendar_tools.calendar_client, 'create_event') as mock_create:
            mock_create.return_value = {
                'success': True,
                'event_id': 'test_event_123',
                'event_type': 'all_day'
            }
            
            result = await calendar_tools.create_event(
                title="Test Event",
                date="2025-05-15",
                description="Test event description"
            )
            
            if "Successfully created" in result:
                print("✅ Calendar event creation test passed")
            else:
                print("❌ Calendar event creation test failed")
                
    except Exception as e:
        print(f"❌ Calendar tools test failed: {e}")

async def test_document_tools(document_tools):
    """Test document tools with mock data."""
    print("📄 Testing document tools...")
    
    try:
        # Mock the AI analysis to avoid actual OpenAI API calls
        with patch.object(document_tools.ai_analysis, 'analyze_document') as mock_analyze:
            mock_analyze.return_value = {
                'success': True,
                'result': {
                    'summary': 'This is a test summary',
                    'key_points': ['Point 1', 'Point 2'],
                    'important_dates': ['2025-05-15'],
                    'action_items': ['Complete task 1']
                }
            }
            
            result = await document_tools.analyze_document(
                "This is a test document for analysis.",
                "summary"
            )
            
            if "Document Summary" in result:
                print("✅ Document analysis test passed")
            else:
                print("❌ Document analysis test failed")
                
    except Exception as e:
        print(f"❌ Document tools test failed: {e}")

async def test_server_imports():
    """Test that the main server components can be imported."""
    print("🖥️ Testing server component imports...")
    
    try:
        # Test individual components instead of full server
        from src.config.settings import Settings
        from src.tools.announcements import AnnouncementTools
        from src.tools.calendar import CalendarTools
        from src.tools.documents import DocumentTools
        
        print("✅ All server components imported successfully")
        print("ℹ️  Note: Full MCP server requires 'mcp' package for production use")
            
    except Exception as e:
        print(f"❌ Server component import failed: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting SchoolConnect MCP Server Tests\\n")
    
    # Test configuration
    settings = await test_configuration()
    if not settings:
        print("\\n❌ Tests failed - configuration issues")
        return
    
    print()
    
    # Test tool initialization
    announcement_tools, calendar_tools, document_tools = await test_tool_initialization(settings)
    if not all([announcement_tools, calendar_tools, document_tools]):
        print("\\n❌ Tests failed - tool initialization issues")
        return
    
    print()
    
    # Test individual tools
    await test_announcement_tools(announcement_tools)
    print()
    await test_calendar_tools(calendar_tools)
    print()
    await test_document_tools(document_tools)
    print()
    
    # Test server imports
    await test_server_imports()
    
    print("\\n🎉 All tests completed!")
    print("\\n📋 Next steps:")
    print("1. Set up your .env file with real credentials")
    print("2. Test with a real MCP client (like Claude Desktop)")
    print("3. Verify Airtable and n8n webhook connectivity")

if __name__ == "__main__":
    asyncio.run(main())

