
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
# get connetion string from .env file
load_dotenv()
connection_string = os.getenv("MONGO_CONNECTION_STRING")
# Connect to MongoDB
client = MongoClient(connection_string)
db = client['brightbound']
collection = db['leads']

# Define the schema
lead_schema = {
    'name': str,
    'company': str,
    'website_url': str,
    'linkedIn_url': str,
    'email': str,
    'icp': str,
    'offer': str,
    'offer_specific': bool,
    'website_summary': str,
    'linkedIn_summary': str,
    'lead_valid': bool,
    'lead_status': str,
    'email_formats': list,
    'created': str,
    'last_updated': str,
    'contacted': str,
    'campaign_id': ObjectId

}
email_format_schema = {
    "email_format": str,
    "personalization": str,
    "icp": str,
    "offer": str,
    "body": str,
    "call_to_action": str
}

# now we need some retrieval functions
# get all leads
def get_all_leads():
    return collection.find()
# get all contacted leads of a certain status
def get_leads_by_status(status):
    return collection.find({"lead_status": status})

def get_leads_by_campaign(campaign_id):
    return collection.find({"campaign_id": campaign_id}) 

def get_contacted_leads_by_campaign(campaign_id):
    return collection.find({"campaign_id": campaign_id, "contacted": {"$exists": True}})

