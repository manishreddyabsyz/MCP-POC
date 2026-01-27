
from __future__ import annotations

import os
import sys

if __package__ is None:  # running as a script: `python backend/api.py`
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

from tools.ask_tool import ask, salesforce_health
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None


@app.post("/query")
def query_endpoint(req: QueryRequest):
    """Query endpoint that uses MCP tools"""
    return ask(req.query, session_id=req.session_id or "default")


@app.get("/health/salesforce")
def salesforce_health_endpoint():
    """Health check using MCP tool"""
    return salesforce_health()
