"""
MCP server entrypoint for cloud deployment.
"""

from __future__ import annotations

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add backend to path
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from tools.ask_tool import mcp


if __name__ == "__main__":
    print("🚀 Salesforce MCP POC running...")
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"  # Required for Railway
    
    print(f"🌐 Server starting on {host}:{port}")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    try:
        # Run MCP server with HTTP transport for cloud deployment
        mcp.run(transport="sse", host=host, port=port)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

