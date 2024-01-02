import AI.summarize as summarizer
import AI.emailWriter as emailWriter
import scraper.scraper as scraper
import linkedin.getLinkedInInfo as linkedin
import csv
import services_and_db.leads.leadService as Leads
import services_and_db.clients.clientMongo as Clients
from concurrent.futures import ThreadPoolExecutor, as_completed

def batchEnrichList(rows, progress_bar, status_text, batch_size=5):
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
        

def singleBatchEnrichmentRun(batch, executor, context):
    future_to_row = {executor.submit(enrichRow, row, context): row for row in batch}
    for future in as_completed(future_to_row):
        enriched_row = future.result()
        if enriched_row is not None:
            Leads.updateLead(enriched_row)

def enrichMongoDB(progress_bar, status_text):
    unenriched_leads = Leads.get_unenriched_leads()
    batchEnrichList(unenriched_leads, progress_bar, status_text)


def enrichRow(row, context):
    #part 1: get the linkedin profile
    linkedin_profile = linkedin.getLinkedInInfo(row['linkedIn_url'])
    if linkedin_profile is None:
        return None # TODO: add something to show that lead is stooopid
    #part 2: get the website content
    website_content = scraper.scrape_website_task(row['website_url'])
    if website_content is None:
        return None
    # part 3: summarize the linkedin profile
    linkedin_summary = summarizer.summarizeProfileData(linkedin_profile)
    # part 4: summarize the website content
    website_summary = summarizer.summarizeWebsiteContent(website_content, context[row['client_id']])
    
    # part 5: return the new row
    row['linkedin_summary'] = linkedin_summary
    row['website_summary'] = website_summary['summary']
    row['icp'] = website_summary['icp']
    row['offer'] = website_summary['offer']
    return row


def writeEmailForEntry(row, product_context,**kwargs):
    outputFormat = kwargs.get('outputFormat', None)
    resultJson = emailWriter.writeEmail(row['first_name'], row['company'], row['linkedin_summary'], row['website_summary'], product_context, outputFormat)
    #iterate over the keys and add them to the row
    for key in resultJson.keys():
        row[key] = resultJson[key]
    return row
