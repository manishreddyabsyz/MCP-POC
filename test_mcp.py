try:
    from mcp.server.fastmcp import FastMCP
    print("✅ MCP import successful!")
    mcp = FastMCP()
    print("✅ FastMCP instance created successfully!")
except ImportError as e:
    print(f"❌ MCP import failed: {e}")