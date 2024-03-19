from services_and_db.leads.LeadObjectConverter import *
import AI.emailWriter as emailWriter
import services_and_db.leads.leadService as Leads
from concurrent.futures import ThreadPoolExecutor, as_completed
def createEmailsForLeadsByTemplate(client, leads, chosen_campaign, progress_bar, status_text, batch_size=10, perfect=False):
    total_leads = len(leads)
    for start_index in range(0, total_leads, batch_size):
        end_index = min(start_index + batch_size, total_leads)
        batch = leads[start_index:end_index]

        # Set up the ThreadPoolExecutor for the current batch
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            singleBatchEmailCreationRun(batch, executor, chosen_campaign, client, perfect=perfect)
        update_progress(progress_bar, start_index, end_index, total_leads, status_text)

def update_progress(progress_bar, start_index, end_index, total_leads, status_text):
    progress = end_index / total_leads
    progress_bar.progress(progress)
    status_text.text(f"Processed rows {start_index + 1} to {end_index} of {total_leads}")
def singleBatchEmailCreationRun(batch, executor, template, client, perfect):
    future_to_row = {executor.submit(writeEmailSequenceFromTemplate_DefaultPersonalization, row, template, client): row for row in batch}
    for future in as_completed(future_to_row):
        enriched_row = future.result()
        if enriched_row is not None:
            Leads.updateLead(enriched_row)

def writeEmailSequenceFromTemplate(lead, template, client, perfect):

    client_context = client['company_summary']
    emails = template['emails']
    for i in range(len(emails)):
        emails[i]['number'] = i+1
    emails = [email for email in emails if email['useAI']]
    lead['campaign_id'] = template['_id']
    field_keys = set()  # Initialize an empty set to store unique field keys
    campaign_context = {}
    if perfect:
        try:
            campaign_context['perfect'] = emailWriter.writeTheBestBrightBoundEmail(lead, client)
        except:
            RuntimeError(f"Error writing the best brightbound email for {lead['company']}")
    email_template = emailWriter.emailTemplateWriterForLead(leadForEmailWriter(lead))
    usedGPT4 = False
    print("number of emails: ", len(emails))
    if len(emails) != 0:
        try:
            campaign_context = emailWriter.writeEmailFieldsFromCampaignAndLeadInfoFromFormat(emails, client_context, leadForEmailWriter(lead), model ="gpt4") 
            lead = extractFields(campaign_context, lead, field_keys, email_template)
        except:
            usedGPT4 = True
            campaign_context = emailWriter.writeEmailFieldsFromCampaignAndLeadInfoFromFormat(emails, client_context, leadForEmailWriter(lead), model ="gpt4") 
            lead = extractFields(campaign_context, lead, field_keys, email_template)
    else:
        lead = extractFields(campaign_context, lead, field_keys, email_template)
    fields = lead['email_fields']
    error = False
    for key in fields.keys():
        if fields[key] == "" or fields[key] == None:
            error = True

    lead = confirm_email_structure(lead, template, client_context, emails, field_keys, email_template, usedGPT4, error)
    return lead

def writeEmailSequenceFromTemplate_DefaultPersonalization(lead, template, client):
    personalization_data = {"website": lead.get('interestings', None),
                            "linkedin": lead.get('linkedin_summary', None)}
    print(personalization_data)
    client_context = client['company_summary']
    emails = template['emails']
    for i in range(len(emails)):
        emails[i]['number'] = i+1
    emails = [email for email in emails if email['useAI']]
    lead['campaign_id'] = template['_id']
    field_keys = set()  # Initialize an empty set to store unique field keys
    campaign_context = {}
    personalization = emailWriter.writePersonalization(lead, client, personalization_data)
    if len(emails) != 0:
        try:
            campaign_context = emailWriter.writeEmailFieldsFromCampaignAndLeadInfoFromFormat(emails, client_context, leadForEmailWriter(lead), model ="gpt4") 
            lead = extractFields(campaign_context, lead, field_keys,None)
        except:
            lead['to_be_fixed'] = True
            return lead
    else:
        lead = extractFields(campaign_context, lead, field_keys, None)
    campaign_context['personalization'] = personalization
    fields = lead['email_fields']
    error = False
    for key in fields.keys():
        if fields[key] == "" or fields[key] == None:
            error = True

    # lead = confirm_email_structure(lead, template, client_context, emails, field_keys, None, True, error)
    return lead


def confirm_email_structure(lead, template, client_context, emails, field_keys, email_template, usedGPT4, error):
    validation_result = emailValidation(lead, template, client_context)
    
    if not all(result['valid'] for result in validation_result) or error:
        lead['to_be_fixed'] = True
        lead['error'] = validation_result
    return lead

def extractFields(campaign_context, lead, field_keys, email_template):
    email_fields = {}
    if campaign_context.get("emails", None) is not None:
        for email_dict in campaign_context["emails"]:
            for email_id, email_content in email_dict.items():
                fields = email_content.get("fields", {})
                field_keys.update(fields.keys())
        
        # Process each field
        for field in field_keys:
            # Iterate through each email to set the field
            for email_dict in campaign_context["emails"]:
                for email_id, email_content in email_dict.items():
                    fields = email_content.get("fields", {})
                    if field in fields:
                        # Add the field and its value to email_fields
                        email_fields[field] = fields[field]
    if campaign_context.get("perfect", None) is not None:
        for key in campaign_context["perfect"].keys():
            email_fields[key] = campaign_context["perfect"][key]
    email_fields['emailTemplate'] = email_template
    lead['campaign_context'] = campaign_context
    lead['email_fields'] = email_fields
    return lead

def emailValidation(lead, campaign,client_context):
    personalized_emails = populateCampaignForLead(lead, campaign)
    return emailWriter.validateEmailsForLead(leadForEmailWriter(lead), personalized_emails, client_context)

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
    return personalized_email_bodies