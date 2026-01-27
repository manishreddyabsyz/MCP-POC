"""
MCP server entrypoint for cloud deployment.
"""

from __future__ import annotations

import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add backend to path
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from tools.ask_tool import mcp, ask, salesforce_health

# Create FastAPI app for health checks and HTTP endpoints
app = FastAPI(title="Salesforce MCP Server")

@app.get("/")
async def root():
    return {"message": "Salesforce MCP Server is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    try:
        # Test Salesforce connection
        sf_health = salesforce_health()
        return {
            "status": "healthy",
            "mcp_server": "running",
            "salesforce": sf_health
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "mcp_server": "running",
                "salesforce": "connection_failed"
            }
        )

@app.post("/ask")
async def ask_endpoint(request: dict):
    """HTTP endpoint for MCP ask tool"""
    try:
        user_query = request.get("user_query", "")
        session_id = request.get("session_id", "default")
        result = ask(user_query, session_id)
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    print("🚀 Salesforce MCP POC running...")
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"  # Required for Railway
    
    print(f"🌐 Server starting on {host}:{port}")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    try:
        # Run FastAPI server with uvicorn for Railway
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

