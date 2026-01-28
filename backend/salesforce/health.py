from __future__ import annotations

from backend.salesforce.connection import sf


def ping() -> dict:
    """
    Lightweight connectivity check.
    Returns a small subset of Salesforce identity info if auth works.
    """
    try:
        # Test connection with a simple query that should always work
        user_query = sf.query("SELECT Id, Name, Username FROM User WHERE Id = UserInfo.getUserId() LIMIT 1")
        
        if user_query and user_query.get('records'):
            user = user_query['records'][0]
            return {
                "type": "salesforce_health",
                "ok": True,
                "user_id": user.get("Id"),
                "username": user.get("Username"),
                "display_name": user.get("Name"),
                "status": "connected",
                "message": f"✅ Connected to Salesforce as {user.get('Name', 'Unknown User')}"
            }
        else:
            # Fallback: just test basic connectivity
            org_query = sf.query("SELECT Id, Name FROM Organization LIMIT 1")
            if org_query and org_query.get('records'):
                org = org_query['records'][0]
                return {
                    "type": "salesforce_health",
                    "ok": True,
                    "organization_id": org.get("Id"),
                    "organization_name": org.get("Name"),
                    "status": "connected_basic",
                    "message": f"✅ Connected to Salesforce org: {org.get('Name', 'Unknown Org')}"
                }
            
    except Exception as e:
        # Get more detailed error information
        error_details = {
            "type": "salesforce_health",
            "ok": False,
            "error_type": type(e).__name__,
            "error": str(e),
            "status": "connection_failed"
        }
        
        # Check if it's an authentication vs authorization issue
        if "NOT_FOUND" in str(e):
            error_details["message"] = "❌ Salesforce resource not found - check API permissions"
            error_details["likely_cause"] = "API user lacks permissions or wrong endpoint"
        elif "INVALID_LOGIN" in str(e):
            error_details["message"] = "❌ Invalid Salesforce credentials"
            error_details["likely_cause"] = "Wrong username/password/security token"
        elif "INVALID_DOMAIN" in str(e):
            error_details["message"] = "❌ Invalid Salesforce domain"
            error_details["likely_cause"] = "Wrong domain (login vs test vs custom)"
        else:
            error_details["message"] = f"❌ Failed to connect to Salesforce: {str(e)}"
        
        return error_details


def test_connection_details():
    """
    Detailed connection test for debugging
    """
    import os
    
    return {
        "sf_username": os.getenv("SF_USERNAME", "NOT_SET"),
        "sf_domain": os.getenv("SF_DOMAIN", "NOT_SET"), 
        "sf_password_set": "YES" if os.getenv("SF_PASSWORD") else "NO",
        "sf_token_set": "YES" if os.getenv("SF_SECURITY_TOKEN") else "NO",
        "connection_url": f"https://{os.getenv('SF_DOMAIN', 'login')}.salesforce.com"
    }

