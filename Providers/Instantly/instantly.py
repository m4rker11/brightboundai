import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.environ["INSTANTLY_API_KEY"]

def get_lead_info(email):

    url = "https://api.instantly.ai/api/v1/lead/get"
    headers = {'Content-Type': 'application/json'}
    payload = {"api_key": api_key, "email": email}
    response = requests.get(url, headers=headers, params=payload)
    return json.loads(response.text)

def lead_ok(email):
    try:
        lead = get_lead_info(email)
        if lead:
            # if lead is a dict and has property error, ignore it
            if isinstance(lead, dict) and lead.get('error', False):
                return True
            else:
                status = lead[0].get('status', None)
                verification = lead[0].get('verification_status', None)
                if verification == 1:
                    return True
                if status == "Bounced" or status == "Unsubscribed" or verification == -2 or verification == 1:
                    return False
                else:   
                    return True
    except:
        return True