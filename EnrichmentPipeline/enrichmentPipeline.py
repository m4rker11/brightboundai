import AI.summarize as summarizer
from services_and_db.leads.LeadObjectConverter import *
from websiteEnrichment import enrichWebsite
from socialEnrichment import process_linkedin_profiles
from ..linkedin.getLinkedInInfo import getLinkedInProxyCurl
from ..services_and_db.leads.leadService import get_leads_for_linkedin_enrichment, updateLead
from ..AI.summarize import summarizeProfileData
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from emailEnrichment import singleBatchEmailCreationRun
import services_and_db.leads.leadService as Leads
import services_and_db.clients.clientMongo as Clients
from concurrent.futures import ThreadPoolExecutor, as_completed

def batchEnrichList(rows, progress_bar, status_text, batch_size=1):
    total_rows = len(rows)
    # Process rows in batches
    clients = Clients.get_all_clients()
    context = {client['_id']: client['company_summary'] for client in clients}
    for start_index in range(0, total_rows, batch_size):
        end_index = min(start_index + batch_size, total_rows)
        batch = rows[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
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
            enriched_row = future.result()
        except:
            print(future)
            print("Timeout enriching a row")
            enriched_row = None
        if enriched_row is not None:
                Leads.updateLead(enriched_row)

def enrichMongoDB(progress_bar, status_text):
    unenriched_leads = Leads.get_unenriched_leads()
    batchEnrichList(unenriched_leads, progress_bar, status_text)


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

def batchEnrichLinkedinProfiles(profiles, progress_bar, status_text, batch_size=5):
    total_profiles = len(profiles)
    for start_index in range(0, total_profiles, batch_size):
        end_index = min(start_index + batch_size, total_profiles)
        batch = profiles[start_index:end_index]
        with asyncio.TaskGroup() as tg:
            for profile in batch:
                tg.create(process_linkedin_profiles(profile))
            asyncio.run(tg)
        update_progress(progress_bar, start_index, end_index, total_profiles, status_text)