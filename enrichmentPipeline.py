import AI.summarize as summarizer

import difflib
import AI.emailWriter as emailWriter
import scraper.scraper as scraper
import linkedin.getLinkedInInfo as linkedin
import services_and_db.leads.leadService as Leads
import services_and_db.clients.clientMongo as Clients
from concurrent.futures import ThreadPoolExecutor, as_completed

def batchEnrichList(rows, progress_bar, status_text, batch_size=15):
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
        try:
            enriched_row = future.result(timeout=100)
        except:
            print("Timeout enriching a row")
            enriched_row = stoopifyLead(enriched_row)
        if enriched_row is not None:
                print(Leads.updateLead(enriched_row))

def enrichMongoDB(progress_bar, status_text):
    unenriched_leads = Leads.get_unenriched_leads()
    batchEnrichList(unenriched_leads, progress_bar, status_text)


def enrichRow(row, context):
    
    # part 1: get the website content
    bestUrl = chooseBestUrl(row)
    website_content = scraper.scrape_website(bestUrl)
    if website_content is None:
        print(f"Website content of {row['company']} is none")
        return stoopifyLead(row)
    
    # Await the summarizeWebsiteContent function to ensure it completes before proceeding
    try:
        website_summary = summarizer.summarizeWebsiteContent(website_content, context[row['client_id']])
    except:
        return stoopifyLead(row)
    if website_summary is None:
        print(f"Website summary of {row['company']} is none")
        return stoopifyLead(row)
    row['website_summary'] = website_summary['summary']
    row['icp'] = website_summary['icp']
    row['offer'] = website_summary['offer']
    if not isBtoB(website_summary['icp']):
        print(f"Website {row['company']} is not B2B")
        return stoopifyLead(row)
        
    # part 2: get the linkedin profile
    try:
        linkedin_profile = linkedin.getLinkedInInfo(row['linkedIn_url'])
    except:
        return stoopifyLead(row)
    if linkedin_profile is None:
        print(f"Linkedin profile of {row['company']} is none")
        return stoopifyLead(row)
    
    # part 3: summarize the linkedin profile
    try:
        linkedin_summary = summarizer.summarizeProfileData(linkedin_profile)
    except:
        return stoopifyLead(row)
    # part 5: return the new row
    row['linkedin_summary'] = linkedin_summary
    
    return row

def isBtoB(icp):
    ICP_keywords = [
    "business", "industry", "enterprise", 
    "corporate", "decision-makers", "procurement", 
    "stakeholders", "partnerships", "operations", 
    "solutions", "supply chain", "integration", 
    "volume", "commercial", "wholesale", "retail",
    ]
    lowercased_icp = icp.lower()
    #check if the icp contains any of the keywords
    for keyword in ICP_keywords:
        if keyword in lowercased_icp:
            return True
    return False


def stoopifyLead(row):
    row['ignore'] = True
    return row

def chooseBestUrl(row):
    # row is a dictionary that may or may not have a website_url and email field
    # we want to return the best url to scrape from

    email = row.get('email', None)
    website_url = row.get('website_url', None)
    company_name = row.get('company', None)  

    emailDomain = email.split('@')[1]
    if not website_url:
        return emailDomain
    elif emailDomain in website_url:
        return website_url
    else:
        return max([website_url, emailDomain], key=lambda x: compute_similarity(x, company_name))

def compute_similarity(input_string, reference_string):
        diff = difflib.ndiff(input_string, reference_string)
        diff_count = 0
        for line in diff:
            if line.startswith("-"):
                diff_count += 1
        return 1 - (diff_count / len(input_string))


def createEmailsForLeadsByTemplate(client, leads, chosen_campaign, progress_bar, status_text, batch_size=5):
    total_leads = len(leads)
    for start_index in range(0, total_leads, batch_size):
        end_index = min(start_index + batch_size, total_leads)
        batch = leads[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            singleBatchEmailCreationRun(batch, executor, chosen_campaign, client)
        progress = end_index / total_leads
        progress_bar.progress(progress)
        status_text.text(f"Processed rows {start_index + 1} to {end_index} of {total_leads}")
        
def singleBatchEmailCreationRun(batch, executor, template, client):
    future_to_row = {executor.submit(writeEmailSequenceFromTemplate, row, template, client): row for row in batch}
    for future in as_completed(future_to_row):
        enriched_row = future.result()
        if enriched_row is not None:
            Leads.updateLead(enriched_row)

def writeEmailSequenceFromTemplate(lead, template, client):

    client_context = client['company_summary']
    emails = template['emails']
    emails = [email for email in emails if email['useAI']]

    fields = emailWriter.writeEmailFieldsFromCampaignAndLeadInfoFromFormat(emails, client_context, lead) #TODO
    for field in fields.keys():
        if field in lead.keys():
            fields.pop(field)
    lead['email_fields'] = fields
    validation_result = emailValidation(lead, template, client_context)
    if not all(result['valid'] for result in validation_result):
        lead = fixEmails(lead, validation_result, template, client_context)
    return lead

def emailValidation(lead, campaign,client_context):
    personalized_emails = populateCampaignForLead(lead, campaign)
    return emailWriter.validateEmailsForLead(lead, personalized_emails, client_context)

def populateCampaignForLead(lead, campaign):
    fields = lead['email_fields']
    emails = campaign['emails']
    email_bodies = [email['body'] for email in emails]
    personalized_email_bodies = []
    for email in email_bodies:
        # each email is a string with a key in {key} format, so we need to replace the key with the value from fields
        for key in lead.keys():
            email = email.replace("{"+key+"}", lead[key] if type(lead[key]) is str else str(lead[key]))
        for key in fields.keys():
            email = email.replace("{"+key+"}", fields[key] if type(fields[key]) is str else str(fields[key]))
        # remove all curly brackets
        email = email.replace("{", "")
        email = email.replace("}", "")
        personalized_email_bodies.append(email)
    return personalized_email_bodies

def fixEmails(lead, validation_result, campaign, client_context):
    print("THERE WAS AN ERROR")
    print(validation_result)
    emails = campaign['emails']
    emails = [email for email in emails if email['useAI']]
    print(emails)
    print(lead['email_fields'])
    print(lead['_id'])
    return lead