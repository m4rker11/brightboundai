from Providers.wiza.wiza_api_wrapper import WizaAPI
import pandas as pd
import time
wiza = WizaAPI()
def get_contacts_dataframe(list_id: str, segment: str):
    print("list done")
    success = False
    while not success:
        try:
            contacts = wiza.get_list_contacts(list_id, segment)
            success = True
            print("Got contacts")
        except:
            print("Failed to get contacts. Retrying in 60 seconds.")
            time.sleep(60)
    return pd.DataFrame(contacts)

def get_contacts_from_client_name_and_group_name(list_id, segment="people"):
    status = False
    while not status:
        response = wiza.get_list(list_id)['data']
        if response['finished_at'] is not None:
            status = True
        else: 
            print("Waiting for Wiza to finish processing the list.")
            time.sleep(60)
    return get_contacts_dataframe(list_id, segment)


def populate_existing_with_linkedin_data(leads):

    all_leads = []
    if len(leads) > 2500:
        batches = [leads[i:i + 2500] for i in range(0, len(leads), 2500)]
        for batch in batches:
            id = wiza.post_new_list(batch)
            if id == None:
                return None
            leads = get_contacts_from_client_name_and_group_name(id, "people")
            all_leads.extend(leads)
    else:
        id = wiza.post_new_list(leads)
        if id == None:
            return None
        leads = get_contacts_from_client_name_and_group_name(id, "people")
        all_leads.extend(leads)
    return all_leads
    
