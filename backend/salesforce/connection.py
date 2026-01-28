import os

from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

# Debug: Print connection details (remove passwords)
username = os.getenv("SF_USERNAME")
domain = os.getenv("SF_DOMAIN", "login")
print(f"Connecting to Salesforce: {username} @ {domain}")

try:
    sf = Salesforce(
        username=username,
        password=os.getenv("SF_PASSWORD"),
        security_token=os.getenv("SF_SECURITY_TOKEN"),
        domain=domain,
    )
    print("✅ Salesforce connection initialized")
except Exception as e:
    print(f"❌ Salesforce connection failed: {e}")
    raise

