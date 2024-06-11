from services_and_db.leads.LeadObjectConverter import *
import pandas as pd
import numpy as np
from Providers.wiza.wiza_service import get_contacts_from_client_name_and_group_name, populate_existing_with_linkedin_data
from EnrichmentPipeline.websiteEnrichment import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from AI.summarize import summarizeProfileData
import time
import json
from Providers.Instantly.instantly import lead_ok
from EnrichmentPipeline.emailEnrichment import singleBatchEmailCreationRun
import services_and_db.leads.leadService as Leads
import services_and_db.clients.clientMongo as Clients

def batchEnrichList(rows, batch_size=10):
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
        
def update_progress(progress_bar, start_index, end_index, total_leads, status_text):
    progress = end_index / total_leads
    progress_bar.progress(progress)
    status_text.text(f"Processed rows {start_index + 1} to {end_index} of {total_leads}")

def singleBatchEnrichmentRun(batch, executor, context):
    future_to_row = {executor.submit(enrichRow, row, context): row for row in batch}
    for future in as_completed(future_to_row):
        try:
            enriched_row = future.result(timeout=60)
        except Exception as e:
            print(future)
            
            print("An error occurred in singleBatchEnrichmentRun:", str(e))
            print("Timeout enriching a row") 
            break
        if enriched_row is not None:
            print("Updating lead ", enriched_row['_id'])
            Leads.updateLead(enriched_row)

def enrichMongoDB(client_id = None):
    if client_id is None:
        unenriched_leads = Leads.get_unenriched_leads()
    else:
        unenriched_leads = Leads.get_unenriched_leads_by_client_id(client_id)
    # no_linkedin_leads = [lead for lead in unenriched_leads if lead.get('linkedin_data', None) is None]
    # if no_linkedin_leads:
    #     print("Populating existing leads with linkedin data, we have ", len(no_linkedin_leads), " leads to enrich.")

    #     # no_linkedin_leads = populate_existing_with_linkedin_data(no_linkedin_leads)
    #     if no_linkedin_leads:
    #         try:
    #             print("Uploading leads to database")
    #             # upload_leads(data=no_linkedin_leads)
    #             # if client_id is not None:
    #             #     unenriched_leads = Leads.get_unenriched_leads_by_client_id(client_id)
    #             # else:
    #             #     unenriched_leads = Leads.get_unenriched_leads()
    #         except Exception as e:
    #             print("An error occurred in enriching linkedin data:", str(e))
    #             return
    #     else:
    #         print("OOPS! Something went wrong while enriching linkedin data.")
    #         return
    batchEnrichList(unenriched_leads)


def enrichRow(row, context):   
    try:
        if row.get('linkedin_data', None) is not None and row.get('linkedin_summary', None) is None:
            row['linkedin_summary'] = summarizeProfileData(clean_empty(row['linkedin_data']))
        if row.get('website_summary', None) is None:
            row = enrichWebsite(row, context)

    except Exception as e:
        print("An error occurred in enrhichRow:", str(e))
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


def async_upload_leads(data, client_name, group, client_id):
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(upload_leads, data, client_name, group, client_id)


def upload_leads(data=None, client_name=None, group=None, client_id=None, list_id=None):
    if data is None and list_id is not None:
        data = get_contacts_from_client_name_and_group_name(list_id)
        data['client_id'] = client_id
        data['group'] = group
        print("We have ", len(data), " from ", list_id)
    data = map_data_to_schema(data)
    Leads.addLeadsFromDataFrame(data)
    # verify_risky_leads_with_instantly()
    enrichMongoDB()



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
    data['linkedIn_url'] = data.get('linkedin', None).apply(process_linkedin_url)
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
    data['linkedin_data'] = clean_empty(data['linkedin_data'])
    
    return data

def clean_empty(d):
    #if it is a dataframe series, then clean empty each element
    if isinstance(d, pd.Series):
        return d.apply(clean_empty)
    if isinstance(d, str):
        try:
            d = json.loads(d)
        except:
            return d
    if isinstance(d, dict):
        return {
            k: v 
            for k, v in ((k, clean_empty(v)) for k, v in d.items())
            if v
        }
    if isinstance(d, list):
        return [v for v in map(clean_empty, d) if v]
    return d


def verify_risky_leads_with_instantly():
    # get all leads that don't have risky parameter set:
    leads = Leads.get_leads_without_risk()
    counter = 0
    good_counter = 0
    for lead in leads:
        time.sleep(0.11)
        email = lead['email']
        # print(lead)
        if lead_ok(email):
            lead['risk'] = False
            good_counter += 1
            print(f"Lead {email} is not risky. {good_counter} leads are good so far.")
        else:
            counter += 1
            lead['risk'] = True
            lead['ignore'] = True
            print(f"Lead {email} is risky, ignoring it. {counter} leads ignored so far.")
        Leads.updateLead(lead)