from services_and_db.leads.LeadObjectConverter import *
from EnrichmentPipeline.websiteEnrichment import *
from EnrichmentPipeline.socialEnrichment import getLinkedInProxyCurl
from concurrent.futures import ThreadPoolExecutor, as_completed
from AI.summarize import summarizeProfileData
import time
from EnrichmentPipeline.emailEnrichment import singleBatchEmailCreationRun
import services_and_db.leads.leadService as Leads
import services_and_db.clients.clientMongo as Clients
from concurrent.futures import ThreadPoolExecutor, as_completed

def batchEnrichListWithWebsite(rows, progress_bar, status_text, batch_size=20):
    total_rows = len(rows)
    # Process rows in batches
    clients = Clients.get_all_clients()
    context = {client['_id']: client['company_summary'] for client in clients}
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

def createEmailsForLeadsByTemplate(client, leads, chosen_campaign, progress_bar, status_text, batch_size=10, perfect=False):
    total_leads = len(leads)
    for start_index in range(0, total_leads, batch_size):
        end_index = min(start_index + batch_size, total_leads)
        batch = leads[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            singleBatchEmailCreationRun(batch, executor, chosen_campaign, client, perfect=perfect)
        update_progress(progress_bar, start_index, end_index, total_leads, status_text)

def fetch_and_update(profile):

    url = profile.get('linkedIn_url')
    print(url)
    if url:
        

        profile_info = getLinkedInProxyCurl(url)
        print(profile_info)
        profile['linkedInPage'] = profile_info
        profile['linkedInSummary'] = summarizeProfileData(profile_info)
        print(profile['linkedInSummary'])
        updateLead(profile)

def singleBatchLinkedinEnrichmentRun(batch, executor):
    future_to_profile = {executor.submit(fetch_and_update, profile): profile for profile in batch}
    for future in as_completed(future_to_profile):
        try:
            future.result(timeout=60)
        except:
            print("Timeout enriching a row")
            pass

def fetch_and_update_profiles(profiles, progress_bar, status_text):
    batch_size = 5  # Maximum number of URLs to process at once


    for start_index in range(0, len(profiles), batch_size):
        end_index = min(start_index + batch_size, len(profiles))
        current_batch = profiles[start_index:end_index]

        # Create a list of coroutines for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            singleBatchLinkedinEnrichmentRun(current_batch, executor)

        # Update the progress on the Streamlit UI
        update_progress(progress_bar, start_index, end_index, len(profiles), status_text)
