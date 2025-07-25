# SchoolConnect MCP Server Setup Guide

This guide will walk you through setting up the SchoolConnect MCP server to work with AI assistants like Claude Desktop.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
- **Access to your school's Airtable database** with API credentials
- **n8n webhook URL** for Google Calendar integration
- **OpenAI API key** for document analysis
- **Claude Desktop** or another MCP-compatible client

## Step 1: Download and Install

### Option A: Clone from GitHub (Recommended)
```bash
git clone https://github.com/vimarshsub/schoolconnect-mcp-server.git
cd schoolconnect-mcp-server
```

### Option B: Download ZIP
1. Download the ZIP file from GitHub
2. Extract to a folder like `schoolconnect-mcp-server`
3. Open terminal/command prompt in that folder

## Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# For production use, also install MCP
pip install mcp
```

## Step 3: Configure Environment Variables

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your actual credentials:
   ```bash
   # Open .env in your text editor
   nano .env  # or use any text editor
   ```

3. **Fill in your credentials:**
   ```env
   # Your Airtable API key (get from https://airtable.com/account)
   AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
   
   # Your Airtable base ID (from your base URL)
   AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
   
   # Your OpenAI API key (get from https://platform.openai.com/api-keys)
   OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   
   # Your n8n webhook URL for calendar integration
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/calendar
   
   # Optional: Set log level (DEBUG, INFO, WARNING, ERROR)
   LOG_LEVEL=INFO
   ```

### Finding Your Credentials

#### Airtable API Key
1. Go to https://airtable.com/account
2. Click "Generate API key"
3. Copy the key (starts with "key")

#### Airtable Base ID
1. Go to your Airtable base
2. Look at the URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Copy the part that starts with "app"

#### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with "sk-")

#### n8n Webhook URL
1. This should be the same URL you're using in your existing backend
2. Check your GitHub secrets or n8n workflow configuration

## Step 4: Test the Server

Run the test script to verify everything is working:

```bash
python test_server.py
```

You should see output like:
```
🚀 Starting SchoolConnect MCP Server Tests
🔧 Testing configuration...
✅ Configuration validation passed
🛠️ Testing tool initialization...
✅ All tool classes initialized successfully
...
🎉 All tests completed!
```

## Step 5: Configure Claude Desktop

### macOS Setup

1. **Find your Claude Desktop config file:**
   ```bash
   open ~/Library/Application\ Support/Claude/
   ```

2. **Edit or create `claude_desktop_config.json`:**
   ```json
   {
     "mcpServers": {
       "schoolconnect": {
         "command": "python",
         "args": ["/full/path/to/schoolconnect-mcp-server/server.py"],
         "env": {
           "AIRTABLE_API_KEY": "keyXXXXXXXXXXXXXX",
           "AIRTABLE_BASE_ID": "appXXXXXXXXXXXXXX",
           "OPENAI_API_KEY": "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
           "N8N_WEBHOOK_URL": "https://your-n8n-instance.com/webhook/calendar"
         }
       }
     }
   }
   ```

### Windows Setup

1. **Find your Claude Desktop config file:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Use the same JSON structure as macOS** but with Windows-style paths:
   ```json
   {
     "mcpServers": {
       "schoolconnect": {
         "command": "python",
         "args": ["C:\\path\\to\\schoolconnect-mcp-server\\server.py"],
         "env": {
           "AIRTABLE_API_KEY": "keyXXXXXXXXXXXXXX",
           "AIRTABLE_BASE_ID": "appXXXXXXXXXXXXXX",
           "OPENAI_API_KEY": "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
           "N8N_WEBHOOK_URL": "https://your-n8n-instance.com/webhook/calendar"
         }
       }
     }
   }
   ```

### Important Notes for Claude Desktop Config

- **Use full absolute paths** - relative paths may not work
- **Replace `/full/path/to/` with your actual path** to the server
- **Use your actual credentials** - don't copy the example values
- **Restart Claude Desktop** after making changes

## Step 6: Test with Claude Desktop

1. **Restart Claude Desktop** completely
2. **Start a new conversation**
3. **Test the tools:**

   ```
   Search for announcements about "field trip"
   ```

   ```
   Get announcements from last week
   ```

   ```
   Create a calendar event for "Parent Teacher Conference" on 2025-02-15
   ```

4. **Look for the 🔧 tool icon** in Claude's interface - this indicates MCP tools are available

## Troubleshooting

### Common Issues

#### "No module named 'mcp'"
```bash
pip install mcp
```

#### "Missing required environment variables"
- Check that your `.env` file exists and has all required variables
- Verify the file is in the same directory as `server.py`
- Make sure there are no extra spaces around the `=` signs

#### "Failed to connect to Airtable"
- Verify your `AIRTABLE_API_KEY` is correct
- Check that your `AIRTABLE_BASE_ID` matches your actual base
- Ensure your API key has permission to access the base

#### "Calendar event creation failed"
- Verify your `N8N_WEBHOOK_URL` is correct and accessible
- Check that your n8n workflow is running and properly configured
- Test the webhook URL directly with a tool like curl

#### "Claude Desktop doesn't show tools"
- Restart Claude Desktop completely
- Check the config file path and JSON syntax
- Verify the server path is absolute and correct
- Check Claude Desktop's logs for error messages

### Debug Mode

Enable debug logging to see detailed information:

```bash
export LOG_LEVEL=DEBUG
python server.py
```

### Testing Individual Components

Test specific functionality:

```bash
# Test configuration only
python -c "from src.config.settings import Settings; s = Settings(); s.validate(); print('Config OK')"

# Test Airtable connection
python -c "from src.integrations.airtable_client import AirtableClient; from src.config.settings import Settings; s = Settings(); s.validate(); client = AirtableClient(s.get_airtable_config()); print('Airtable OK')"
```

## Next Steps

Once everything is working:

1. **Explore the available tools** - see README.md for full documentation
2. **Customize the configuration** - adjust settings in `src/config/settings.py`
3. **Monitor the logs** - check for any errors or warnings
4. **Share with your team** - others can use the same setup

## Getting Help

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Review the troubleshooting section** above
3. **Test individual components** to isolate the problem
4. **Create an issue** on GitHub with:
   - Your operating system
   - Python version
   - Error messages
   - Steps to reproduce

## Security Notes

- **Keep your `.env` file secure** - never commit it to version control
- **Use environment-specific API keys** for development vs production
- **Regularly rotate your API keys** for security
- **Limit API key permissions** to only what's needed

## Updates

To update the MCP server:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

Then restart Claude Desktop to pick up any changes.

