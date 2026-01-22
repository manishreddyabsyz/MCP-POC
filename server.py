from mcp.server.fastmcp import FastMCP
from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os
load_dotenv()
mcp=FastMCP()
sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_SECURITY_TOKEN"),
    domain=os.getenv("SF_DOMAIN", "login")
)
if __name__ == "__main__":
    mcp.run()