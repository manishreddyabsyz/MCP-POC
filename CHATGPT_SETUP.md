# ChatGPT Desktop + MCP Setup Guide

This guide shows how to connect ChatGPT Desktop to your Salesforce MCP server for intelligent case analysis.

## Prerequisites

1. **ChatGPT Desktop App** (with MCP support)
2. **Your MCP server running** 
3. **Salesforce credentials configured** in `backend/.env`

## Setup Steps

### 1. Start Your MCP Server

```bash
# From your project root
python backend/server.py
```

You should see: `🚀 Salesforce MCP POC running...`

### 2. Configure ChatGPT Desktop

1. Open ChatGPT Desktop
2. Go to Settings → Beta Features → Enable MCP
3. Add MCP Server Configuration:

**Server Name:** `salesforce-agent`
**Command:** `python`
**Arguments:** `["backend/server.py"]`
**Working Directory:** `C:\Users\Manish Reddy\Desktop\MCP POC`

Or copy the config from `mcp-config.json` in this project.

### 3. Test the Connection

In ChatGPT Desktop, try these commands:

```
Check Salesforce connection
```

```
Show me case 12345
```

```
List all in progress cases
```

## Available Commands

ChatGPT can now intelligently respond to:

### Case Queries
- "Show me details for case 12345"
- "What's the status of case 12345?"
- "Summarize case 12345"

### Case Comments & History
- "Show comments for case 12345"
- "What's the history of changes for case 12345?"
- "Show the feed activity for case 12345"

### Case Search & Lists
- "Find cases about login issues"
- "List all cases in progress"
- "Search for cases with 'password reset'"

### Analysis & Insights
- "Analyze the troubleshooting steps for case 12345"
- "What are the next actions needed for case 12345?"
- "Summarize the technical issues in case 12345"

## What ChatGPT Can Do

With access to your Salesforce data, ChatGPT can:

✅ **Retrieve case information** in natural language
✅ **Analyze case patterns** and suggest solutions  
✅ **Summarize complex cases** with key insights
✅ **Track case progress** and identify bottlenecks
✅ **Search across cases** with intelligent filtering
✅ **Provide context-aware recommendations**

## Example Conversation

**You:** "Show me the most critical in-progress cases"

**ChatGPT:** *Uses your MCP tools to fetch in-progress cases, analyzes priority levels, and presents a summary with recommendations*

**You:** "What's the history of case 12345?"

**ChatGPT:** *Retrieves case history, identifies key changes, and explains the case progression in natural language*

## Troubleshooting

### MCP Server Not Found
- Ensure `python backend/server.py` runs without errors
- Check that your working directory is correct in ChatGPT settings

### Salesforce Connection Issues  
- Verify your `.env` file has correct SF credentials
- Test with: "Check Salesforce connection"

### No Case Data
- Ensure your Salesforce user has proper permissions
- Try a simple query first: "Show me case [known_case_number]"