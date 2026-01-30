# Custom GPT Actions & Schema Explained

## 🎯 What is `custom-gpt-schema.json`?

The `custom-gpt-schema.json` file is an **OpenAPI 3.0 specification** that acts as a "contract" between ChatGPT and your Salesforce API. It tells ChatGPT:

- 📍 **Where** your API is located (server URL)
- 🔧 **What** endpoints are available 
- 📝 **How** to call each endpoint
- 📊 **What** data to send and expect back

Think of it as a **"manual"** that ChatGPT reads to understand how to use your API.

---

## 🔍 Code Breakdown - Section by Section

### 1. **Header Information**
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Salesforce Case Assistant API",
    "description": "API for querying Salesforce cases with natural language", 
    "version": "1.0.0"
  }
}
```

**What it does:**
- 📋 **openapi**: Tells ChatGPT this follows OpenAPI 3.0 standard
- 🏷️ **title**: Name shown in ChatGPT's action list
- 📝 **description**: Explains what this API does
- 🔢 **version**: API version for tracking changes

---

### 2. **Server Configuration**
```json
"servers": [
  {
    "url": "https://your-deployment-url.com",
    "description": "Production server"
  }
]
```

**What it does:**
- 🌐 **url**: The base URL where your API is deployed
- 📍 **description**: Human-readable server description

**⚠️ Important**: You must replace `https://your-deployment-url.com` with your actual deployment URL (Railway, Heroku, etc.)

---

### 3. **API Endpoints (Paths)**

The `paths` section defines what ChatGPT can do with your API:

#### **A. Query Endpoint (`/query`)**
```json
"/query": {
  "post": {
    "summary": "Query Salesforce cases with natural language",
    "operationId": "querySalesforce"
  }
}
```

**What it does:**
- 🎯 **Endpoint**: `POST /query` 
- 📝 **Purpose**: Main endpoint for case queries
- 🆔 **operationId**: Unique identifier ChatGPT uses internally

#### **B. Request Body Schema**
```json
"requestBody": {
  "required": true,
  "content": {
    "application/json": {
      "schema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Natural language query about Salesforce cases"
          },
          "session_id": {
            "type": "string", 
            "description": "Optional session identifier",
            "default": "default"
          }
        },
        "required": ["query"]
      }
    }
  }
}
```

**What it does:**
- 📨 **Tells ChatGPT**: "Send JSON data in this format"
- 🔤 **query** (required): The user's natural language question
- 🆔 **session_id** (optional): For conversation tracking
- ✅ **required**: Only "query" field is mandatory

**Example request ChatGPT will send:**
```json
{
  "query": "Show me case 12345",
  "session_id": "chatgpt-session-123"
}
```

#### **C. Response Schema**
```json
"responses": {
  "200": {
    "description": "Successful response with case data or analysis",
    "content": {
      "application/json": {
        "schema": {
          "type": "object",
          "properties": {
            "type": { "type": "string" },
            "session_id": { "type": "string" },
            "message": { "type": "string" },
            "case_data": { "type": "object" }
          }
        }
      }
    }
  }
}
```

**What it does:**
- 📥 **Tells ChatGPT**: "Expect JSON response in this format"
- 🏷️ **type**: Response category (case_data, clarification, etc.)
- 💬 **message**: Human-readable response
- 📊 **case_data**: Structured Salesforce data

#### **D. Health Check Endpoint (`/health/salesforce`)**
```json
"/health/salesforce": {
  "get": {
    "summary": "Check Salesforce connection health",
    "operationId": "checkSalesforceHealth"
  }
}
```

**What it does:**
- 🏥 **Endpoint**: `GET /health/salesforce`
- ✅ **Purpose**: Verify Salesforce connection is working
- 🔧 **No parameters**: Simple GET request

---

## 🤖 How Custom GPT Actions Work

### **Step-by-Step Process:**

1. **👤 User asks ChatGPT**: "Show me case 12345"

2. **🧠 ChatGPT analyzes**: 
   - "This sounds like a Salesforce query"
   - "I should use the querySalesforce action"

3. **📡 ChatGPT calls your API**:
   ```http
   POST https://your-app-url.com/query
   Content-Type: application/json
   
   {
     "query": "Show me case 12345",
     "session_id": "gpt-session-abc123"
   }
   ```

4. **🔄 Your API processes**:
   - Extracts case number "12345"
   - Queries Salesforce
   - Returns structured data

5. **📨 Your API responds**:
   ```json
   {
     "type": "case_data",
     "session_id": "gpt-session-abc123", 
     "message": "Found case 12345",
     "case_data": {
       "CaseNumber": "12345",
       "Subject": "Login Issues",
       "Status": "In Progress",
       "Priority": "High"
     }
   }
   ```

6. **🎨 ChatGPT formats response**:
   - Takes the raw API data
   - Formats it nicely for the user
   - Shows case details in readable format

---

## 🛠️ Setting Up Actions in Custom GPT

### **Step 1: Create Custom GPT**
1. Go to [ChatGPT](https://chat.openai.com)
2. Click **"Explore GPTs"** → **"Create a GPT"**
3. Fill in basic info:
   - **Name**: "Salesforce Case Assistant"
   - **Description**: "Query Salesforce cases with natural language"

### **Step 2: Add Actions**
1. Click **"Configure"** tab
2. Scroll to **"Actions"** section
3. Click **"Create new action"**
4. **Copy entire `custom-gpt-schema.json` content** and paste it
5. **Update the server URL** to your actual deployment
6. Set **Authentication** to **"None"**
7. Click **"Save"**

### **Step 3: Test Actions**
ChatGPT will now show available actions:
- ✅ **querySalesforce**: For case queries
- ✅ **checkSalesforceHealth**: For health checks

---

## 🎯 What Actions Enable

### **Without Actions (Regular ChatGPT):**
- ❌ Can't access your Salesforce data
- ❌ Can only provide general advice
- ❌ No real-time information

### **With Actions (Your Custom GPT):**
- ✅ **Live Salesforce data**: Real case information
- ✅ **Natural language**: "Show me case 12345" works
- ✅ **Structured responses**: Formatted case details
- ✅ **Context awareness**: Remembers conversation
- ✅ **Multiple operations**: Cases, comments, search, etc.

---

## 🔧 Action Flow Examples

### **Example 1: Case Lookup**
```
User: "Show me details for case 12345"
↓
ChatGPT: Calls querySalesforce action
↓  
API: Returns case data
↓
ChatGPT: "Here are the details for case 12345:
- Subject: Login Issues
- Status: In Progress  
- Priority: High
- Created: 2024-01-15"
```

### **Example 2: Health Check**
```
User: "Is Salesforce working?"
↓
ChatGPT: Calls checkSalesforceHealth action
↓
API: Returns connection status
↓
ChatGPT: "✅ Salesforce connection is healthy. 
All systems operational."
```

### **Example 3: Error Handling**
```
User: "Show me case 99999"
↓
ChatGPT: Calls querySalesforce action
↓
API: Returns "case not found" 
↓
ChatGPT: "I couldn't find case 99999. 
Please check the case number and try again."
```

---

## 🚀 Benefits of This Approach

### **For Users:**
- 🗣️ **Natural language**: No need to learn Salesforce syntax
- ⚡ **Fast access**: Get case info in seconds
- 🤖 **AI assistance**: ChatGPT helps interpret data
- 📱 **Always available**: Works from any device

### **For Developers:**
- 🔌 **Easy integration**: Standard OpenAPI format
- 🛡️ **Secure**: No API keys exposed to ChatGPT
- 🔄 **Flexible**: Can add new endpoints easily
- 📊 **Structured**: Clear request/response format

---

## 🔒 Security Considerations

### **What's Secure:**
- ✅ **No credentials in schema**: API keys stay on your server
- ✅ **HTTPS only**: Encrypted communication
- ✅ **Controlled access**: Only defined endpoints exposed

### **What to Watch:**
- ⚠️ **Public Custom GPT**: Anyone with link can use it
- ⚠️ **Rate limiting**: Consider adding API limits
- ⚠️ **Data sensitivity**: Ensure appropriate case access

---

## 🎯 Summary

The `custom-gpt-schema.json` file is the **bridge** between ChatGPT and your Salesforce API:

1. **📋 Defines** what ChatGPT can do with your API
2. **🔧 Specifies** how to format requests and responses  
3. **🤖 Enables** natural language interaction with Salesforce
4. **🚀 Powers** the Custom GPT to provide real-time case data

Without this schema, ChatGPT would be just a regular chatbot. With it, ChatGPT becomes a **powerful Salesforce assistant** that can query live data and provide intelligent responses!