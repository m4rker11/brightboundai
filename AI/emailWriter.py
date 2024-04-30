from AI.base import invoke_chain

def writeEmailFieldsFromCampaignAndLeadInfoFromFormat(email_templates, client_context, lead) -> dict:
    prompt_template ="""
    EMAIL TEMPLATES:
    '''
    {email_templates}
    '''
    Lead Info:
    ''
    {lead_info}
    ''
    Client Context:
    '
    {client_context}
    '
    You are writing a sequence of emails to send to {lead_name} from {lead_company}. Here are the rules you have to follow.
    Rules:
    1. The keys in the json object must be the same as the fields from the email templates shown as {{curly brackets}} in the email templates.
    2. The values in the json object must be the personalized information from the lead.
    3. When the values are plugged in to the email templates, the resulting emails should be the final personalized email to the lead.
    4. The emails are written with the goal of bringing the lead in for a conversation with the client, the description of the client is in the client context.
    5. When the values are plugged in to the email templates, the resulting emails should be coherent and sound human.
    6. Output only the json object as the response starting and ending with curly brackets. Your output will be treated as a valid json object.
    7. If a field has a word count limit, do not exceed the limit.
    8. The output json format should be the following:
    {{emails: [
        {{1: {{
            "subject": "subject of email 1",
            "body": "full email if fields are plugged in to the template",
            "fields": {{
                "field1": "value1",
                "field2": "value2"
            }}
        }} #etc for the rest of the emails
    ]}}
    
    OUTPUT:
    """
    return invoke_chain(model="gpt-4", temperature=0.2,
                        prompt_template=prompt_template, output_parser="json",
                        data = {"email_templates": email_templates,
                            "lead_info": lead,
                            "client_context": client_context,
                            "lead_name": lead['first_name'],
                            "lead_company": lead['company']})


def validateEmailsForLead(lead, campaign, client_context)->dict:
    prompt_template = """
    EMAILS:
    '''
    {emails}
    '''
    Lead Info:
    ''
    {lead_info}
    ''
    Client Context:
    '
    {client_context}
    '
    You are verifying that the sequence of emails to send to {lead_name} from {lead_company} is valid and a good email. Here are the rules you have to follow.
    Rules:
    1. Your Output must be a valid json object. it should be a list of json objects, each json object corresponds to an email in the sequence.
    2. The json object must have a key "valid" with a boolean value.
    3. If the value of "valid" is false, field "reason" must be present with a string value explaining why the email is invalid.
    4. If the value of "valid" is true, field "reason" must not be present.
        The following is the validity criteria for an email:
        a. The email must be coherent and sound human.
        b. The email must be personalized to the lead.
        c. The email should not make any strong assumptions and rely only on the lead information and the client context, slight exageration is ok.
        d. The email should be under 150 words.
        e. There should be no random capitalization.
        f. The email must make complete sense and not be at all confusing.
    5. The list should be in the same order as the emails in the sequence and of the same length.
    6. The emails are written with the goal of bringing the lead in for a conversation with the client, the description of the client is in the client context.

    OUTPUT:
    """
    return invoke_chain(model="gpt-3.5", temperature=0.2,
                        prompt_template=prompt_template, output_parser="json",
                        data = {"emails": campaign,
                            "lead_info": lead,
                            "client_context": client_context,
                            "lead_name": lead['first_name'],
                            "lead_company": lead['company']})