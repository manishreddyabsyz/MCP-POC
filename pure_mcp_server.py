#!/usr/bin/env python3
"""
Pure MCP server (no HTTP wrapper)
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

from tools.ask_tool import mcp

if __name__ == "__main__":
    print("🚀 Pure MCP Server starting...")
    print("This runs ONLY MCP protocol (no HTTP)")
    print("Only MCP clients can connect (not Custom GPT)")
    
    # Run pure MCP server
    mcp.run()  # This is pure MCP protocol