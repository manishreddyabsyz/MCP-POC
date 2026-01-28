from __future__ import annotations

from backend.salesforce.connection import sf


def ping() -> dict:
    """
    Lightweight connectivity check.
    Returns a small subset of Salesforce identity info if auth works.
    """
    try:
        # Test connection with a simple query first
        sf.query("SELECT Id FROM User LIMIT 1")
        
        # Get identity information
        ident = sf.identity
        return {
            "user_id": ident.get("user_id"),
            "organization_id": ident.get("organization_id"), 
            "username": ident.get("username"),
            "display_name": ident.get("display_name"),
            "status": "connected"
        }
    except Exception as e:
        # If identity fails, try a different approach
        try:
            # Alternative: get current user info
            user_info = sf.query("SELECT Id, Name, Username FROM User WHERE Id = UserInfo.getUserId() LIMIT 1")
            if user_info and user_info['records']:
                user = user_info['records'][0]
                return {
                    "user_id": user.get("Id"),
                    "username": user.get("Username"),
                    "display_name": user.get("Name"),
                    "status": "connected_alt_method"
                }
        except:
            pass
        
        raise e

