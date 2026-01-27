from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from agent.agent_core import handle_user_query
from agent.memory import MemoryStore

mcp = FastMCP()
_memory = MemoryStore()


@mcp.tool()
def ask(user_query: str, session_id: str = "default"):
    return handle_user_query(user_query=user_query, session_id=session_id, memory=_memory)


@mcp.tool()
def salesforce_health():
    """
    Check Salesforce connectivity using the configured SF_* environment variables.
    """
    from backend.salesforce.health import ping

    return {"type": "salesforce_health", "ok": True, "identity": ping()}
