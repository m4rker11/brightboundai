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
    "fields": object,
    "useAI": bool,
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
    return result.inserted_id

def update_campaign_by_id(campaign_id, campaign):
    """
    Updates a campaign by id
    """
    result = collection.update_one({"_id": campaign_id}, {"$set": campaign})
    return result.upserted_id

