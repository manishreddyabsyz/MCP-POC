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
SF_USERNAME=gellasangamesh95@fieldservice.com
SF_PASSWORD=Disang_1124
SF_SECURITY_TOKEN=7IVzj7cMbm0pObgb751p9fTeo
SF_DOMAIN=login
OPENAI_API_KEY=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
```

## 5. Deploy

Click "Create Web Service" and Render will deploy your app.

You'll get a URL like: `https://your-app-name.onrender.com`