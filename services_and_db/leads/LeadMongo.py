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
    'first_name': str,
    'company': str,
    'website_url': str,
    'linkedIn_url': str,
    'email': str,
    'icp': str,
    'offer': str,
    'city': str,
    'job_title': str,
    'keywords': list,
    'industry': str,
    'company_country': str,
    'company_state': str,
    'company_linkedin_url': str,
    'employees': int,
    'offer_specific': bool,
    'website_summary': str,
    'website_content': dict,
    'linkedin_summary': str,
    'lead_valid': bool,
    'lead_status': str,
    'email_fields': dict,
    'created': str,
    'last_updated': str,
    'contacted': str,
    'campaign_context':dict,
    'campaign_id': ObjectId,
    'ignore': bool,
    'to_be_fixed': bool,
    'client_id': ObjectId,
    'batch_id': ObjectId,
    'group': str,
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
            lead.pop(key)

    required_fields = ['email', 'linkedIn_url', 'first_name']
    for field in required_fields:
        if field not in lead or lead[field] is None:
            print(f"Lead {lead['full_name']} is missing required field {field}")
            return False

    return True  # If all checks pass, the lead is valid


# now we need some retrieval functions
# get all leads
def get_all_leads():
    return list(collection.find())
# get all contacted leads of a certain status

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

def get_lead_by_email(email):
    return collection.find_one({"email": email})

def get_unenriched_leads() -> list:
    return list(collection.find({"website_summary": {"$exists": False},
                            "ignore": {"$ne": True}}))

def get_leads_for_linkedin_enrichment() -> list:
    return list(collection.find({"linkedin_summary": {"$exists": False},
                            "ignore": {"$ne": True}}))

def get_leads_by_client_id(client_id):
    return list(collection.find({"client_id": ObjectId(client_id), "ignore": {"$ne": True}}))

def get_fully_enriched_leads_by_client_id(client_id):
    return list(collection.find({"client_id": ObjectId(client_id), "ignore": {"$ne": True}, "linkedin_summary": {"$exists": True}, "website_summary": {"$exists": True}}))

def get_leads_by_batch_id(batch_id):
    return list(collection.find({"batch_id": ObjectId(batch_id), "ignore": {"$ne": True}}))

def get_leads_by_campaign_id(campaign_id):
    return list(collection.find({"campaign_id": ObjectId(campaign_id), "ignore": {"$ne": True}, "to_be_fixed": {"$ne": True}}))

def check_if_lead_exists(email, website, client_Id) -> bool:
    #check if lead with email or website exists by client id returns true if exists
    return collection.find_one({"$or": [{"email": email}, {"website_url": website}], "client_id": ObjectId(client_Id)}) != None
