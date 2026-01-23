from tools.ask_tool import mcp
from agent.validator import validate_query
from agent.router import route_query

if __name__ == "__main__":
    print("🚀 Salesforce MCP POC running...")
    mcp.run()
