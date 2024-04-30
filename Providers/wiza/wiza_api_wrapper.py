import os
import requests

class WizaAPI:
    def __init__(self):
        self.api_key = os.getenv('WIZA_API_KEY')
        if not self.api_key:
            raise ValueError("API key not found. Set the WIZA_API_KEY environment variable.")

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

    def get_list_contacts(self, list_id):
        """Retrieve contacts of a specific list."""
        url = f"{self.base_url}/{list_id}/contacts?segment=valid"
        response = requests.get(url, headers=self.headers)
        return response.json()['data']