
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
    'full_name': str,
    'name': str,
    'company': str,
    'website_url': str,
    'linkedIn_url': str,
    'email': str,
    'icp': str,
    'offer': str,
    'city': str,
    'role': str,
    'offer_specific': bool,
    'website_summary': str,
    'linkedIn_summary': str,
    'lead_valid': bool,
    'lead_status': str,
    'email_formats': list,
    'created': str,
    'last_updated': str,
    'contacted': str,
    'campaign_id': ObjectId,
    'ignore': bool,
}

email_format_schema = {
    "email_format": str,
    "personalization": str,
    "icp": str,
    "offer": str,
    "body": str,
    "call_to_action": str
}
def validate_lead(lead):
    if not isinstance(lead, dict):
        raise ValueError("Lead must be a dictionary")

    # Remove fields not in the schema
    for key in list(lead.keys()):
        if key not in lead_schema:
            lead.pop(key)

    # Check for field types and required fields
    for key, expected_type in lead_schema.items():
        if key in lead and not isinstance(lead[key], expected_type) and lead[key] is not None:
            raise TypeError("Lead field {} must be of type {}".format(key, expected_type))

    required_fields = ['email', 'website_url', 'linkedIn_url', 'name']
    for field in required_fields:
        if field not in lead or lead[field] is None:
            raise ValueError("Lead field {} cannot be None".format(field))

    return True  # If all checks pass, the lead is valid


# now we need some retrieval functions
# get all leads
def get_all_leads():
    return collection.find()
# get all contacted leads of a certain status
def get_leads_by_status(status):
    return collection.find({"lead_status": status, 'ignore': {"$exists": False}})

def get_leads_by_campaign(campaign_id):
    return collection.find({"campaign_id": campaign_id, 'ignore': {"$exists": False}}) 

def get_contacted_leads_by_campaign(campaign_id):
    return collection.find({"campaign_id": campaign_id, "contacted": {"$exists": True}, 'ignore': {"$exists": False}})

def add_lead(lead):
    return collection.insert_one(lead)

def get_lead_by_id(id):
    return collection.find_one({"_id": ObjectId(id)})

def update_lead(id, lead):
    entry = get_lead_by_id(id)
    for key in lead:
        if lead[key] != None:
            entry[key] = lead[key]
    return collection.update_one({"_id": ObjectId(id)}, {"$set": entry})

def delete_lead(id):
    return collection.delete_one({"_id": ObjectId(id)})

def ignore_lead(id):
    return collection.update_one({"_id": ObjectId(id)}, {"$set": {"ignore": True}})

def get_lead_by_email(email):
    return collection.find_one({"email": email})

def get_unenriched_leads() -> list:
    return list(collection.find({"website_summary": {"$exists": False},
                            "linkedIn_summary": {"$exists": False}}))
                            