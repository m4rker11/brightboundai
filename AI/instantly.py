import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("INSTANTLY_API_KEY")

def get_emails():
    url = "https://api.instantly.ai/api/v1/unibox/emails/"
    headers = {'Content-Type': 'application/json'}
    payload = {}
    response = requests.get(url, headers=headers, params={'api_key': api_key}, data=json.dumps(payload))
    return response.text

def get_unread_emails_count():
    url = "https://api.instantly.ai/api/v1/unibox/emails/count/unread"
    headers = {'Content-Type': 'application/json'}
    payload = {}
    response = requests.get(url, headers=headers, params={'api_key': api_key}, data=json.dumps(payload))
    return response.text

def mark_thread_as_read(thread_id):
    url = f"https://api.instantly.ai/api/v1/unibox/threads/{thread_id}/mark-as-read"
    headers = {'Content-Type': 'application/json'}
    payload = {"api_key": api_key}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.text

def respond_to_email(thread_id, response):
    url = f"https://api.instantly.ai/api/v1/unibox/threads/{thread_id}/reply"
    headers = {'Content-Type': 'application/json'}
    payload = {"api_key": api_key, "response": response}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.text

