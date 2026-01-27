import os

from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()
print(os.getenv("SF_USERNAME"),os.getenv("SF_DOMAIN", "login"),os.getenv("SF_PASSWORD"))
sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_SECURITY_TOKEN"),
    domain=os.getenv("SF_DOMAIN", "login"),
)

