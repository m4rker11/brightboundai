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
collection = db['clients']

client_schema = {
    "name": str,
    "email": str,
    "company_name": str,
    "company_website": str,
    "company_industry": str,
    "company_summary": dict,
    "company_emails": list,
    "company_fees": str,
    "icp": str,
    
}

def get_client_by_name(name):
    """
    Gets a client by company name
    """
    client = collection.find_one({"company_name": name})
    return client

def get_client_by_id(id):
    """
    Gets a client by id
    """
    client = collection.find_one({"_id": ObjectId(id)})
    return client

def create_client(client):
    """
    Creates a client
    """
    result = collection.insert_one(client)
    return result.acknowledged

def update_client(id, client):
    """
    Updates a client
    """
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": client})
    return result.acknowledged

def get_all_clients():
    """
    Gets all clients
    """
    clients = collection.find()
    return clients