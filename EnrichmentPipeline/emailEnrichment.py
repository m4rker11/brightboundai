from services_and_db.leads.LeadObjectConverter import *
import AI.emailWriter as emailWriter
from AI.summarize import summarizePersonalizationData, inferFinancialGoals
import services_and_db.leads.leadService as Leads
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json

# Error tracking setup
error_counter = {'count': 0}
error_lock = threading.Lock()
errored_entries = []

def createEmailsForLeadsByTemplate(client, leads, chosen_campaign, progress_bar, status_text, batch_size=3):
    total_leads = len(leads)
    for start_index in range(0, total_leads, batch_size):
        end_index = min(start_index + batch_size, total_leads)
        batch = leads[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(singleBatchEmailCreationRun, batch, executor, chosen_campaign, client) for batch in batches]
            for future in as_completed(futures):
                result = future.result()
                if result == "Stopping due to too many errors":
                    print("Too many errors encountered. Here are the errored entries:")
                    # save errored entries to a errors.json file
                    with open('errors.json', 'w') as f:
                        json.dump(errored_entries, f)
                    break
        update_progress(progress_bar, start_index, end_index, total_leads, status_text)

def update_progress(progress_bar, start_index, end_index, total_leads, status_text):
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
    personalization_data = {"first_name": lead.get('first_name', "Not available"),
                            "website": lead.get('website_summary', "Not available"),
                            "linkedin": lead.get('linkedin_summary', "Not available"),
                            "job_title": lead.get('job_title', "Not available")}
    
    print(personalization_data)
    personalization_data = summarizePersonalizationData(personalization_data, template)
    if client["company_name"] == "Nth Degree CPAs":
        # print("Nth Degree CPAs detected")
        financial_goals = inferFinancialGoals(personalization_data)
        personalization_data+="\n"+financial_goals
    # print("Personalization data for "+lead['first_name']+ " " + str(lead['_id']) + ":")
    # print(personalization_data)
    client_context = client['company_summary']
    emails = template['emails']
    for i in range(len(emails)):
        emails[i]['number'] = i+1
    emails = [email for email in emails if email['useAI']]
    lead['campaign_id'] = template['_id']
    field_keys = set()  # Initialize an empty set to store unique field keys
    campaign_context = {}
    if len(emails) != 0:
        tries = 0
        while tries < 3:
            try:
                campaign_context = emailWriter.writeEmailFieldsFromCampaignAndLeadInfoFromFormat(emails, client_context, leadForEmailWriter(lead, personalization_data)) 
                lead = extractFields(campaign_context, lead, field_keys)
                break
            except:
                tries += 1
        if tries == 3:
            lead['error'] = True
            lead['error_message'] = "Failed to extract fields from campaign context"
            return lead
        lead = extractFields(campaign_context, lead, field_keys)
    fields = lead['email_fields']
    print("Fields for "+lead['first_name']+ " " + str(lead['_id']) + ":")
    print(fields)
    for key in fields.keys():
        if fields[key] == "" or fields[key] == None:
            lead['error'] = True
            lead['error_message'] = "Field is empty: "+key
    if not lead.get("error", False):
        lead = confirm_email_structure(lead, template, personalization_data)
    
    if lead.get("error", False):
        print("#######################################FAULTY EMAIL#######################################")
        print(lead.get("email", lead['_id']), lead.get("error_message", "No error message"))
    

    return lead

def confirm_email_structure(lead, template, pd):
    retry = 0
    while retry<4:
        try:
            if retry ==3:
                validation_result['result'] = False
            else:
                validation_result = emailValidation(lead, template, pd)
            if validation_result['result'] or validation_result['result'] == "True":
                return lead
            else:
                lead['error'] = True
                lead['to_be_fixed'] = True
                lead['error_message'] = validation_result
                return lead
        except:
            retry += 1
    
def emailValidation(lead, campaign, pd):
    personalized_emails = populateCampaignForLead(lead, campaign)
    result = emailWriter.validateEmailsForLead(leadForEmailWriter(lead, pd), personalized_emails)
    # print("Validation result for "+lead['first_name']+ " " + str(lead['_id']) + ":" + str(result))
    return result
def populateCampaignForLead(lead, campaign):
    fields = lead['email_fields']
    emails = campaign['emails']
    email_bodies = [email['body'] for email in emails if email['useAI']]
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
    print(personalized_email_bodies)
    return personalized_email_bodies

def extractFields(campaign_context, lead, field_keys):
    email_fields = {}
    if campaign_context.get("emails", None) is not None:
        for email_dict in campaign_context["emails"]:
            for _, email_content in email_dict.items():
                fields = email_content.get("fields", {})
                field_keys.update(fields.keys())
        
        # Process each field
        for field in field_keys:
            # Iterate through each email to set the field
            for email_dict in campaign_context["emails"]:
                for _, email_content in email_dict.items():
                    fields = email_content.get("fields", {})
                    if field in fields:
                        # Add the field and its value to email_fields
                        email_fields[field] = fields[field]
    if campaign_context.get("perfect", None) is not None:
        for key in campaign_context["perfect"].keys():
            email_fields[key] = campaign_context["perfect"][key]
    lead['campaign_context'] = campaign_context
    lead['email_fields'] = email_fields
    return lead
