from services_and_db.leads.LeadObjectConverter import *
import pandas as pd
import numpy as np
from Providers.wiza.wiza_service import get_contacts_from_client_name_and_group_name
from EnrichmentPipeline.websiteEnrichment import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from AI.summarize import summarizeProfileData
import time
from EnrichmentPipeline.emailEnrichment import singleBatchEmailCreationRun
import services_and_db.leads.leadService as Leads
import services_and_db.clients.clientMongo as Clients

def batchEnrichListWithWebsite(rows, progress_bar, status_text, batch_size=10):
    total_rows = len(rows)
    # Process rows in batches
    clients = Clients.get_all_clients()
    context = {client['_id']: {
        "summary": client['company_summary'],
        "industry": client['company_industry'],
     } for client in clients}
    for start_index in range(0, total_rows, batch_size):
        end_index = min(start_index + batch_size, total_rows)
        batch = rows[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size,) as executor:
            singleBatchEnrichmentRun(batch, executor, context)
        progress = end_index / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Processed rows {start_index + 1} to {end_index} of {total_rows}")
        
def update_progress(progress_bar, start_index, end_index, total_leads, status_text):
    progress = end_index / total_leads
    progress_bar.progress(progress)
    status_text.text(f"Processed rows {start_index + 1} to {end_index} of {total_leads}")

def singleBatchEnrichmentRun(batch, executor, context):
    future_to_row = {executor.submit(enrichRow, row, context): row for row in batch}
    for future in as_completed(future_to_row):
        try:
            enriched_row = future.result(timeout=60)
        except:
            print(future)
            print("Timeout enriching a row")
            enriched_row = None
        if enriched_row is not None:
            print("Updating lead ", enriched_row['_id'])
            Leads.updateLead(enriched_row)

def enrichMongoDB(progress_bar, status_text):
    unenriched_leads = Leads.get_unenriched_leads()
    batchEnrichListWithWebsite(unenriched_leads, progress_bar, status_text)


def enrichRow(row, context):   
    try:
        row = enrichWebsite(row, context)
    except:
        return stoopifyLead(row)
    return row


def stoopifyLead(row):
    row['ignore'] = True
    return row

def createEmailsForLeadsByTemplate(client, leads, chosen_campaign, progress_bar, status_text, batch_size=10):
    total_leads = len(leads)
    for start_index in range(0, total_leads, batch_size):
        end_index = min(start_index + batch_size, total_leads)
        batch = leads[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            singleBatchEmailCreationRun(batch, executor, chosen_campaign, client)
        update_progress(progress_bar, start_index, end_index, total_leads, status_text)


def async_upload_leads(data=None, client_name=None, group=None, client_id=None, streamlit=None):
    #upload leads with a single thread and alert when completed
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(upload_leads, data, client_name, group, client_id)
        while not future.done():
            time.sleep(1)
        if streamlit:
            streamlit.toast("Leads uploaded successfully")


def upload_leads(data=None, client_name=None, group=None, client_id=None):
    if data is None and client_name is not None and group is not None and client_id is not None:
        data = get_contacts_from_client_name_and_group_name(client_name, group)
        data['client_id'] = client_id
        data['group'] = group
        
    data = map_data_to_schema(data)
    Leads.addLeadsFromDataFrame(data)



def process_linkedin_url(url):
    #https://www.linkedin.com/sales/people/ACwAAAGmM64BPyPMrd7pVisRnkPLZSMNczczQyU,NAME_SEARCH,pZjt is an example of a sales navigator url
    #we want to take the id in this example ACwAAAGmM64BPyPMrd7pVisRnkPLZSMNczczQyU and attach it to linkedin.com/in/
    if 'linkedin.com' in str(url):
        if 'sales/people' in url:
            url = 'https://www.linkedin.com/in/'+url.split('/')[-1].split(',')[0]
        else:
            url = url
    else:
        url = np.nan
    return url

def create_funding_info(row):
    components = [str(row.get(key)) for key in ['company_last_funding_round', 'company_last_funding_amount', 'company_last_funding_at'] if pd.notna(row.get(key))]
    return ' | '.join(components)

def create_company_info(row):
    components = [str(row.get(key)) for key in ['company_description', 'company_founded', 'company_type', 'company_revenue'] if pd.notna(row.get(key))]
    return ' | '.join(components)

def check_mandatory_columns(data):
    mandatory_columns = ['full_name', 'first_name', 'company', 'website_url', 'linkedIn_url', 'email']
    missing_columns = [col for col in mandatory_columns if col not in data.columns]
    if missing_columns:
        raise Exception(f"Missing mandatory columns: {', '.join(missing_columns)}")
    return data

def add_state_from_region(data):
    if 'company_region' in data.columns and 'company_state' not in data.columns:
        data['company_state'] = data['company_region']
        data = data.drop(columns=['company_region'], errors='ignore')
    return data

def remove_unwanted_columns(data):
    columns_to_remove = ['linkedin', 'domain', 'company_domain', 'company_last_funding_round', 'company_last_funding_amount', 'company_last_funding_at', 'company_description', 'company_founded', 'company_type', 'company_revenue', 'region', 
                         'linkedin_profile_url', 'company_industry', 'company_subindustry', 'company_size_range', 'summary', 'sub_title', 'months_at_current_position', 'months_at_current_company', 
                         'current_job_description', 'work_history', 'skills', 'education', 'certifications', 'person_industry', 'title', 'phone1', 'phone2', 'phone3', 'personal_email1', 'personal_email2', 'personal_email3']
    data = data.drop(columns=columns_to_remove, errors='ignore')
    return data

def map_data_to_schema(data):
    # Mapping columns based on the provided details
    data['linkedIn_url'] = data['linkedin'].apply(process_linkedin_url)
    data['funding_info'] = data.apply(create_funding_info, axis=1)
    data['company_info'] = data.apply(create_company_info, axis=1)
    data['website_url'] = data['company_domain']
    data['employees'] = data['company_size']
    data['city'] = data['company_locality']
    #personal website is domain if it is different from company domain
    data['personal_website'] = data.apply(lambda row: row['domain'] if row['domain'] != row['company_domain'] else np.nan, axis=1)

    linkedin_columns = ['summary', 'work_history', 'skills', 'person_industry', 'current_job_description', 'months_at_current_company', 'education', 'title', 'sub_title', 'certifications']
    data['linkedin_data'] = data[linkedin_columns].apply(lambda row: {col: row[col] for col in linkedin_columns if pd.notna(row[col])}, axis=1)
    data = check_mandatory_columns(data)
    data = add_state_from_region(data)
    # Drop phone numbers and personal email
    data = data.drop(columns=[col for col in data.columns if 'phone' in col or col == 'personal_email1'], errors='ignore')
    data = remove_unwanted_columns(data)
    
    return data
