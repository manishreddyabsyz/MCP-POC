from __future__ import annotations

from backend.salesforce.connection import sf


def ping() -> dict:
    """
    Lightweight connectivity check.
    Returns a small subset of Salesforce identity info if auth works.
    """
    ident = sf.identity()
    return {
        "user_id": ident.get("user_id"),
        "organization_id": ident.get("organization_id"),
        "username": ident.get("username"),
    }

