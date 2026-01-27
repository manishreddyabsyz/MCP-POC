"""
MCP server entrypoint.

Same import-path bootstrap as `backend/api.py` so `python backend/server.py`
works from a fresh shell on Windows.
"""

from __future__ import annotations

import os
import sys

if __package__ is None:  # running as a script: `python backend/server.py`
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

from backend.tools.ask_tool import mcp


if __name__ == "__main__":
    print("🚀 Salesforce MCP POC running...")
    mcp.run()

