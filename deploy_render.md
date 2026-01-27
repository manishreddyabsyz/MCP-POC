# Deploy to Render (GitHub Alternative)

## 1. Create Render Account

Go to [render.com](https://render.com) and sign up with email (no GitHub required).

## 2. Create Web Service

1. Click "New" → "Web Service"
2. Choose "Build and deploy from a Git repository"
3. Connect your repository OR upload files directly

## 3. Configure Service

- **Name**: salesforce-mcp-server
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python backend/server.py`

## 4. Add Environment Variables

In the Environment section, add:

```
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token
SF_DOMAIN=login
OPENAI_API_KEY=your_openai_api_key
```

## 5. Deploy

Click "Create Web Service" and Render will deploy your app.

You'll get a URL like: `https://your-app-name.onrender.com`