from Providers.wiza.wiza_api_wrapper import WizaAPI
from Providers.wiza.wiza_website_wrapper import get_list_id
import pandas as pd
import time
wiza = WizaAPI()
def get_contacts_dataframe(list_id: str):
    contacts = wiza.get_list_contacts(list_id)
    print(contacts)
    return pd.DataFrame(contacts)

def get_contacts_from_client_name_and_group_name(client, group):
    list_id = get_list_id(client, group)
    status = False
    while not status:
        response = wiza.get_list(list_id)['data']
        print(response)
        if response['finished_at'] is not None:
            status = True
        else: 
            time.sleep(60)
    return get_contacts_dataframe(list_id)
