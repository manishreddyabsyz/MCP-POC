#!/usr/bin/env python3
"""
Run pure MCP server (no HTTP wrapper) for testing MCP protocol directly
"""

import os
import sys

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def run_pure_mcp():
    print("🚀 Starting Pure MCP Server...")
    print("This will run the MCP server using stdio transport")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        from tools.ask_tool import mcp
        
        # Run pure MCP server with stdio transport
        print("MCP Server starting with stdio transport...")
        mcp.run()  # This runs the pure MCP protocol server
        
    except KeyboardInterrupt:
        print("\n👋 MCP Server stopped by user")
    except Exception as e:
        print(f"❌ MCP Server failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_pure_mcp()