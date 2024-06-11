import os
import requests
import time
class WizaAPI:
    def __init__(self):
        self.api_key = os.environ.get('WIZA_API_KEY')
        # if not self.api_key:
        #     raise ValueError("API key not found. Set the WIZA_API_KEY environment variable.")

        self.base_url = "https://wiza.co/api/lists"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_list(self, list_id):
        """Retrieve details of a specific list."""
        url = f"{self.base_url}/{list_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_list_contacts(self, list_id, segment="valid"):
        """Retrieve contacts of a specific list."""
        url = f"{self.base_url}/{list_id}/contacts?segment={segment}"
        response = requests.get(url, headers=self.headers)
        return response.json()['data']
    
    def post_new_list(self, leads):
        """Create a new list."""
        url = self.base_url
        name = leads[0].get('group', str(time.time()) + "_" + str(len(leads)))
        enrichment_level = "partial"
        email_options = {
            "accept_work": True,
            "accept_personal": True,
            "accept_generic": False
            }
        items = [{"profile_url": lead.get("linkedIn_url", None)} for lead in leads if lead.get("linkedIn_url", None) is not None]
        payload = {"list": {"name": name, "enrichment_level": enrichment_level, "email_options": email_options, "items": items}}
        print(payload)
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()['data']['id']
        else:
            print(response.text)
            return None