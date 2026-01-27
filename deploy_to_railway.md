# Deploy to Railway - Step by Step

## 1. Prepare Your Repository

Your code is ready for deployment! All necessary files are created.

## 2. Deploy to Railway

### Option A: Using Railway Dashboard (Easiest)

1. **Go to [railway.app](https://railway.app)**
2. **Sign up/Login** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Connect your repository**
6. **Railway will auto-detect Python and deploy**

### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

## 3. Set Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token
SF_DOMAIN=login
OPENAI_API_KEY=your_openai_api_key
```

## 4. Get Your MCP Server URL

After deployment, Railway gives you a URL like:
`https://your-project-name.railway.app`

## 5. Test Your Deployed Server

```bash
curl https://your-project-name.railway.app/health
```

## 6. Configure ChatGPT

### For ChatGPT Desktop:
Create MCP config with your Railway URL:

```json
{
  "mcpServers": {
    "salesforce-agent": {
      "command": "curl",
      "args": ["-X", "POST", "https://your-project-name.railway.app/mcp"],
      "transport": "http"
    }
  }
}
```

### For Custom GPT:
1. Go to ChatGPT → Create Custom GPT
2. Add Action with your Railway URL
3. Configure schema for your MCP tools

## 7. Test Complete Flow

In ChatGPT, try:
- "Check Salesforce connection"
- "Show me case 12345"
- "List in progress cases"

## What You'll Achieve:

```
ChatGPT → Railway (Your MCP Server) → Salesforce → Intelligent Responses
```

This demonstrates the complete MCP loop your manager requested!

## Troubleshooting

### If deployment fails:
- Check Railway logs in dashboard
- Ensure all environment variables are set
- Verify requirements.txt is in root directory

### If MCP connection fails:
- Test server URL directly with curl
- Check ChatGPT MCP configuration
- Verify server is running (check Railway dashboard)

## Cost:
- Railway free tier: $5/month credit (enough for testing)
- Scales automatically based on usage