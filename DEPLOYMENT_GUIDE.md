# MCP Server Cloud Deployment Guide

## Option 1: Deploy to Railway (Recommended)

### 1. Setup Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Install Railway CLI: `npm install -g @railway/cli`

### 2. Deploy Your MCP Server
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables
railway variables set SF_USERNAME="gellasangamesh95@fieldservice.com"
railway variables set SF_PASSWORD="Disang_1124"
railway variables set SF_SECURITY_TOKEN="7IVzj7cMbm0pObgb751p9fTeo"
railway variables set SF_DOMAIN="login"
railway variables set OPENAI_API_KEY="your_openai_key"

# Deploy
railway up
```

### 3. Get Your MCP Server URL
After deployment, Railway will give you a URL like:
`https://your-app-name.railway.app`

## Option 2: Deploy to Render

### 1. Setup Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### 2. Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repo
3. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python backend/server.py`
   - **Environment**: Python 3.11

### 3. Add Environment Variables
In Render dashboard, add:
- `SF_USERNAME`: gellasangamesh95@fieldservice.com
- `SF_PASSWORD`: Disang_1124
- `SF_SECURITY_TOKEN`: 7IVzj7cMbm0pObgb751p9fTeo
- `SF_DOMAIN`: login
- `OPENAI_API_KEY`: your_openai_key

## Option 3: Use ngrok (Quick Testing)

### 1. Install ngrok
Download from [ngrok.com](https://ngrok.com)

### 2. Run Your Server Locally
```bash
python backend/server.py
```

### 3. Expose with ngrok
```bash
ngrok http 8080
```

You'll get a URL like: `https://abc123.ngrok.io`

## Configure ChatGPT with Your Cloud MCP Server

### For ChatGPT Desktop:
```json
{
  "mcpServers": {
    "salesforce-agent": {
      "command": "curl",
      "args": ["-X", "POST", "https://your-deployed-url.railway.app/mcp"],
      "transport": "http"
    }
  }
}
```

### For ChatGPT Web (Custom GPT):
1. Create a Custom GPT
2. Add your MCP server URL as an action
3. Configure authentication if needed

## Test Your Deployed MCP Server

Once deployed, test with:
```bash
curl -X POST https://your-deployed-url.railway.app/tools/ask \
  -H "Content-Type: application/json" \
  -d '{"user_query": "health check", "session_id": "test"}'
```

## What This Achieves

✅ **Complete MCP Loop**: ChatGPT → Cloud MCP Server → Salesforce
✅ **Internet Accessible**: Anyone can use your MCP tools
✅ **Production Ready**: Demonstrates real-world MCP usage
✅ **No Local Dependencies**: Works from any ChatGPT instance