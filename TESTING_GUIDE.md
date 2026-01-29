# Salesforce Case Assistant - Testing Guide

This guide explains how different users can test the Salesforce Case Assistant application.

## 🎯 Testing Methods Overview

| Method | Best For | Technical Level | Setup Time |
|--------|----------|----------------|------------|
| **Custom GPT** | Business users, managers | Low | 5 minutes |
| **Web Interface** | Internal team, developers | Medium | 10 minutes |
| **API Testing** | Technical validation | High | 2 minutes |
| **MCP Client** | MCP protocol testing | High | 15 minutes |

---

## 1. 🤖 Custom GPT Testing (Easiest)

### Setup (One-time)
1. Go to [ChatGPT](https://chat.openai.com) → **"Explore GPTs"** → **"Create a GPT"**
2. **Name**: "Salesforce Case Assistant"
3. **Description**: "Query Salesforce cases with natural language"
4. **Add Actions**:
   - Click **"Create new action"**
   - Copy the entire content from `custom-gpt-schema.json` file
   - **Update the server URL** to your deployment URL
   - **Authentication**: None
   - **Save**

### Test Queries
```
Check Salesforce connection
Show me case 12345
Get comments for case 12345
List all in progress cases
Search for cases about login issues
Get troubleshooting steps for case 00001166
Show me case history for case 12345
```

### Expected Results
- ✅ Connection health check
- ✅ Case details with structured data
- ✅ Comments and history
- ✅ Search results
- ✅ Troubleshooting steps

---

## 2. 🌐 Web Interface Testing

### Setup
```bash
# Terminal 1: Start Backend
cd backend
pip install -r requirements.txt
python api.py

# Terminal 2: Start Frontend  
cd frontend
npm install
npm run dev
```

### Access
- **URL**: http://localhost:5173
- **Interface**: Chat-like interface similar to ChatGPT

### Test Scenarios
1. **Basic Case Lookup**:
   - Type: "Show me case 12345"
   - Expect: Case details with summary, technical analysis

2. **Case Comments**:
   - Type: "Get comments for case 12345"
   - Expect: List of case comments with timestamps

3. **Search Functionality**:
   - Type: "Search for cases about login"
   - Expect: Multiple matching cases

4. **Health Check**:
   - Type: "Check Salesforce connection"
   - Expect: Connection status

---

## 3. 🔧 API Testing (Technical)

### Using curl
```bash
# Health Check
curl -X GET "https://your-app-url.com/health/salesforce"

# Query Cases
curl -X POST "https://your-app-url.com/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me case 12345",
    "session_id": "test-session"
  }'
```

### Using Postman
1. **Import Collection**: Create requests for `/query` and `/health/salesforce`
2. **Set Base URL**: Your deployment URL
3. **Test Cases**:
   - Health check (GET)
   - Case queries (POST with JSON body)

### Sample API Requests
```json
// Basic case lookup
{
  "query": "Show me case 12345",
  "session_id": "api-test"
}

// Case comments
{
  "query": "Get comments for case 12345",
  "session_id": "api-test"
}

// Search cases
{
  "query": "Search for cases about login issues",
  "session_id": "api-test"
}
```

---

## 4. 🔌 MCP Client Testing

### Setup MCP Client
```bash
# Install MCP client tools
pip install mcp

# Test connection to your MCP server
mcp-client --server-url "your-mcp-server-url"
```

### Test MCP Tools
```python
# Use the ask tool directly
ask("Show me case 12345", session_id="mcp-test")

# Use salesforce_health tool
salesforce_health()
```

---

## 🧪 Test Cases & Expected Results

### Core Functionality Tests

| Test Case | Input | Expected Output |
|-----------|-------|----------------|
| **Health Check** | "Check Salesforce connection" | Status: healthy/unhealthy |
| **Case by Number** | "Show me case 12345" | Case details, summary, analysis |
| **Case by ID** | "Show me case 500XXXXXXXXX" | Case details, summary, analysis |
| **Case Comments** | "Get comments for case 12345" | List of comments with timestamps |
| **Case History** | "Show history for case 12345" | Case field changes over time |
| **Search Cases** | "Search for login issues" | Multiple matching cases |
| **List by Status** | "List all in progress cases" | Cases with 'In Progress' status |
| **Invalid Case** | "Show me case 99999" | Error message or clarification |

### Edge Cases

| Test Case | Input | Expected Behavior |
|-----------|-------|------------------|
| **Short Case Number** | "case 123" | Ask for clarification or treat as case number |
| **Invalid Case ID** | "case 500ABC123" | Ask for correct 18-char Case ID |
| **Ambiguous Query** | "show me cases" | Ask for clarification |
| **Empty Query** | "" | Request valid input |

---

## 🚀 Quick Start for Testers

### For Business Users (Non-Technical)
1. **Use Custom GPT** - Easiest option
2. **Follow setup in MANAGER_DEMO_GUIDE.md**
3. **Start with**: "Check Salesforce connection"

### For Developers
1. **Use Web Interface** - Full functionality
2. **Run locally** with backend + frontend
3. **Test API endpoints** directly

### For QA/Testing Teams
1. **Use all methods** for comprehensive testing
2. **Focus on edge cases** and error handling
3. **Test with real Salesforce data**

---

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"Connection failed"** | Check Salesforce credentials in `.env` |
| **"Case not found"** | Verify case exists in your Salesforce org |
| **"Server error"** | Check backend logs, ensure server is running |
| **"CORS error"** | Verify frontend/backend URLs match |

### Debug Steps
1. **Check Health Endpoint**: `/health/salesforce`
2. **Verify Environment**: Salesforce credentials
3. **Check Logs**: Backend console output
4. **Test Simple Query**: "Check connection" first

---

## 📊 Success Metrics

### What Good Testing Looks Like
- ✅ Health check passes
- ✅ Case lookups return structured data
- ✅ Comments and history load correctly
- ✅ Search finds relevant cases
- ✅ Error handling works gracefully
- ✅ Session context maintained across queries

### Performance Expectations
- **Response Time**: < 3 seconds for case lookups
- **Availability**: 99%+ uptime
- **Error Rate**: < 1% for valid queries

---

## 🎯 Next Steps

After testing, users can:
1. **Deploy to production** (Railway, Heroku, etc.)
2. **Share Custom GPT** with team members
3. **Integrate with existing workflows**
4. **Customize for specific use cases**

For deployment help, see deployment documentation or contact the development team.