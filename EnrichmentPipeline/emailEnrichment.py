from services_and_db.leads.LeadObjectConverter import *
import AI.emailWriter as emailWriter
import services_and_db.leads.leadService as Leads
from concurrent.futures import ThreadPoolExecutor, as_completed
def createEmailsForLeadsByTemplate(client, leads, chosen_campaign, progress_bar, status_text, batch_size=10):
    total_leads = len(leads)
    for start_index in range(0, total_leads, batch_size):
        end_index = min(start_index + batch_size, total_leads)
        batch = leads[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            singleBatchEmailCreationRun(batch, executor, chosen_campaign, client)
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
    personalization_data = {"Interesting_bit_from_website": lead.get('interestings', "Nothing interesting found"),
                            "linkedin": lead.get('linkedin_summary', "Not available"),
                            "job_title": lead.get('job_title', "Not available"),
                            "Company_information":{
                                "offer": lead.get('offer', None),
                                "industry": lead.get('industry', None),
                                "icp": lead.get('icp', None),
                                "company_summary": lead.get('website_summary', None),
                                "relevant_to_my_offer": lead.get('selling_points', "Not available")
                            }}
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
                lead = extractFields(campaign_context, lead, field_keys,None)
                break
            except:
                tries += 1
        if tries == 3:
            lead['error'] = True
            return lead
        lead = extractFields(campaign_context, lead, field_keys, None)
    fields = lead['email_fields']
    print(fields)
    for key in fields.keys():
        if fields[key] == "" or fields[key] == None:
            lead["error"] = [{"field": key, "valid": False, "message": "Field is empty"}]
    

    return lead


def extractFields(campaign_context, lead, field_keys, email_template):
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
