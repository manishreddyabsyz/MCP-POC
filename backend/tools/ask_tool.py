from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from agent.agent_core import handle_user_query
from agent.memory import MemoryStore

mcp = FastMCP()
_memory = MemoryStore()


@mcp.tool()
def ask(user_query: str, session_id: str = "default"):
    """
    Query Salesforce cases with natural language. This tool can:
    - Get case details by case number or ID
    - Show case comments, history, and feed
    - Search for cases by keywords
    - List cases by status (e.g., "in progress cases")
    - Provide case summaries and analysis
    
    Examples:
    - "Show me case 12345"
    - "Get comments for case 12345" 
    - "Show history for case 12345"
    - "List all in progress cases"
    - "Search for cases about login issues"
    
    Args:
        user_query: Natural language query about Salesforce cases
        session_id: Session identifier for maintaining conversation context
        
    Returns:
        Structured response with case data, analysis, or search results
    """
    return handle_user_query(user_query=user_query, session_id=session_id, memory=_memory)


@mcp.tool()
def salesforce_health():
    """
    Check Salesforce connectivity and authentication status.
    
    Returns:
        Connection status and user identity information
    """
    from backend.salesforce.health import ping

    try:
        identity = ping()
        return {
            "type": "salesforce_health", 
            "ok": True, 
            "identity": identity,
            "message": f"✅ Connected to Salesforce as {identity.get('display_name', 'Unknown User')}"
        }
    except Exception as e:
        return {
            "type": "salesforce_health",
            "ok": False, 
            "error": f"{type(e).__name__}: {e}",
            "message": "❌ Failed to connect to Salesforce"
        }
