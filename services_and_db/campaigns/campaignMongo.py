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
collection = db['campaigns']

campaign_schema = {
    "name": str,
    "client_id": ObjectId,
    "recepient_count": int,
    "status": dict,
    "emails": list, #list of email schemas
}
email_schema = {
    "subject": str,
    "body": str,
    "call_to_action": str,
    "personalization": str,
    "use_AI": bool,
    "delay": int,
}

def get_campaigns_by_client_id(client_id):
    """
    Gets all campaigns by client_id
    """
    campaigns = collection.find({"client_id": ObjectId(client_id)})
    return campaigns

def get_campaign_by_name(name):
    """
    Gets a campaign by name
    """
    campaign = collection.find_one({"name": name})
    return campaign

def get_campaign_by_id(id):
    """
    Gets a campaign by id
    """
    campaign = collection.find_one({"_id": ObjectId(id)})
    return campaign
def create_campaign(campaign_name, client_id):
    """
    Creates a campaign
    """
    campaign = {
        "name": campaign_name,
        "client_id": ObjectId(client_id)
    }
    result = collection.insert_one(campaign)
    return result.acknowledged

def add_email_to_campaign(id, email):
    """
    Adds an email to a campaign
    """
    result = collection.update_one({"_id": ObjectId(id)}, {"$push": {"emails": email}})
    return result.acknowledged

def add_variant_to_email(id, email_position, variant):
    """
    Adds a variant to an email in list[email_position]
    """
    result = collection.update_one({"_id": ObjectId(id)}, {"$push": {"emails."+str(email_position)+".variants": variant}})
    return result.acknowledged

def remove_variant_from_email(id, email_position, variant_position):
    """
    Removes a variant from an email in list[email_position]
    """
    result = collection.update_one({"_id": ObjectId(id)}, {"$unset": {"emails."+str(email_position)+".variants."+str(variant_position): 1}})
    return result.acknowledged
