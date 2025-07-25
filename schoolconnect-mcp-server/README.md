# SchoolConnect MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with tools to access school announcements, create calendar events, and analyze documents.

## Features

### 🔍 **Intelligent Announcement Search**
- Advanced search with relevance ranking
- Natural language date filtering
- Sender-based filtering
- Stop words filtering to eliminate false matches
- Configurable result limits

### 📅 **Smart Calendar Integration**
- Automatic all-day vs timed event detection
- Google Calendar integration via n8n webhooks
- Reminder creation with customizable timing
- Event validation and formatting

### 📄 **AI-Powered Document Analysis**
- Document summarization
- Event extraction from announcements
- Action item identification with priorities
- Content analysis and categorization

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Access to your school's Airtable database
- n8n webhook for Google Calendar integration
- OpenAI API key for document analysis

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vimarshsub/schoolconnect-mcp-server.git
   cd schoolconnect-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. **Configure your credentials in `.env`:**
   ```bash
   AIRTABLE_API_KEY=your_airtable_api_key_here
   AIRTABLE_BASE_ID=your_airtable_base_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   N8N_WEBHOOK_URL=your_n8n_webhook_url_here
   ```

### Running the Server

```bash
python server.py
```

The server will start and listen for MCP client connections via stdio.

## Using with Claude Desktop

To use this MCP server with Claude Desktop, add the following to your Claude Desktop configuration:

### macOS Configuration
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "schoolconnect": {
      "command": "python",
      "args": ["/path/to/schoolconnect-mcp-server/server.py"],
      "env": {
        "AIRTABLE_API_KEY": "your_airtable_api_key",
        "AIRTABLE_BASE_ID": "your_airtable_base_id", 
        "OPENAI_API_KEY": "your_openai_api_key",
        "N8N_WEBHOOK_URL": "your_n8n_webhook_url"
      }
    }
  }
}
```

### Windows Configuration
Edit `%APPDATA%\\Claude\\claude_desktop_config.json` with the same structure.

## Available Tools

### Announcement Tools

#### `search_announcements`
Search school announcements with intelligent relevance ranking.

**Parameters:**
- `query` (required): Search text to find in announcements
- `sender` (optional): Filter by sender name
- `date_filter` (optional): Natural language date filter
- `limit` (optional): Maximum results (default: 15, max: 50)

**Example:**
```
Search for "field trip" announcements from last month
```

#### `get_announcements_by_date`
Get announcements from a specific date range.

**Parameters:**
- `date_query` (required): Natural language date query
- `limit` (optional): Maximum results (default: 15)

**Example:**
```
Get announcements from May 2025
```

#### `get_recent_announcements`
Get the most recent school announcements.

**Parameters:**
- `limit` (optional): Number of recent announcements (default: 10)

### Calendar Tools

#### `create_calendar_event`
Create a calendar event with automatic type detection.

**Parameters:**
- `title` (required): Event title
- `date` (required): Event date (YYYY-MM-DD)
- `description` (optional): Event description
- `location` (optional): Event location
- `event_type` (optional): "auto", "all_day", or "timed"
- `start_time` (optional): Start time for timed events (HH:MM)
- `duration_hours` (optional): Duration for timed events

**Example:**
```
Create a calendar event for "Field Day" on 2025-05-15
```

#### `create_reminder`
Create a reminder event before a main event.

**Parameters:**
- `title` (required): Main event title
- `main_event_date` (required): Main event date (YYYY-MM-DD)
- `reminder_days_before` (optional): Days before event (default: 3)
- `description` (optional): Additional description

#### `create_event_with_reminder`
Create an event and reminder together.

**Parameters:**
- Combines parameters from `create_calendar_event` and `create_reminder`
- `create_reminder_flag` (optional): Whether to create reminder (default: true)

### Document Analysis Tools

#### `analyze_document`
Analyze a document with AI-powered analysis.

**Parameters:**
- `text` (required): Document text to analyze
- `analysis_type` (optional): "summary", "events", or "action_items"

#### `summarize_announcement`
Create a summary of a school announcement.

**Parameters:**
- `text` (required): Announcement text to summarize

#### `extract_events`
Extract event information from a document.

**Parameters:**
- `text` (required): Document text to analyze

#### `extract_action_items`
Extract action items and tasks from a document.

**Parameters:**
- `text` (required): Document text to analyze

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AIRTABLE_API_KEY` | Your Airtable API key | Yes |
| `AIRTABLE_BASE_ID` | Your Airtable base ID | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `N8N_WEBHOOK_URL` | n8n webhook URL for calendar | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |

### Advanced Configuration

The server includes several configurable settings in `src/config/settings.py`:

- **Search Configuration**: Stop words, relevance scoring
- **Calendar Configuration**: Default event types, time detection
- **Logging Configuration**: Log levels, formatting

## Architecture

```
schoolconnect-mcp-server/
├── server.py                 # Main MCP server
├── src/
│   ├── config/
│   │   └── settings.py       # Configuration management
│   ├── tools/
│   │   ├── announcements.py  # Announcement search tools
│   │   ├── calendar.py       # Calendar event tools
│   │   └── documents.py      # Document analysis tools
│   ├── integrations/
│   │   ├── airtable_client.py # Airtable integration
│   │   ├── calendar_client.py # Calendar integration
│   │   └── ai_analysis.py     # AI analysis integration
│   └── shared/
│       └── utils.py          # Shared utilities
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md               # This file
```

## Integration with Existing Backend

This MCP server is designed to work alongside your existing SchoolConnect backend:

- **Backend**: Handles batch jobs (announcement fetching, calendar sync)
- **MCP Server**: Provides interactive tools for AI assistants
- **Shared Data**: Both access the same Airtable database

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure all required environment variables are set in your `.env` file
   - Check that the `.env` file is in the same directory as `server.py`

2. **"Failed to connect to Airtable"**
   - Verify your `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID` are correct
   - Check that your Airtable API key has the necessary permissions

3. **"Calendar event creation failed"**
   - Verify your `N8N_WEBHOOK_URL` is correct and accessible
   - Check that your n8n workflow is properly configured

4. **"OpenAI API error"**
   - Verify your `OPENAI_API_KEY` is valid and has sufficient credits
   - Check that you have access to the required OpenAI models

### Logging

The server provides detailed logging. To enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python server.py
```

### Testing

Run the test suite:

```bash
pip install -e ".[dev]"
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the logs for detailed error information

## Related Projects

- [SchoolConnect AI Backend](https://github.com/vimarshsub/schoolconnect_ai_backend) - The main backend system
- [Model Context Protocol](https://github.com/anthropics/mcp) - The MCP specification

