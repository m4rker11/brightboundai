from AI.base import invoke_chain
# def writePersonalization(lead, client, personalizationData):
#     output_format = {
#         "first_line": """The first line of the email should be a standalone sentence commenting on the most 
#         interesting and personal part of the PD. 
#         This should be describing the specific this information using specific language used in the PD.
#         It should follow the following format: 
#         "[Great/awesome/super cool/etc] reading about [10 words or less from the PD] on [personalization source]!""",

#         "second_line": """The second line of email should be one sentence that comments on/follows up/elaborates pn/relates to the first line.
#         It should dive deeper into the PD and mentioning more specifics from it.
#         """,

#         "third_line": """A 7-12 word praise specific to the first two lines, using the language from the PD. 
#             Here are some examples: "A benevolent gesture from a simple yet effective approach", 
#             "Sounds similar to a [ironic modifier to [company with similar story] e.g. a small company like Apple"]!",
#             "Solving important problems, one person at a time, love it!"
#             """,

#         "Subject": """Based on the first and second line of the email, write the subject for the email in 5-8 words.  
#         Using the language from the PD, create a subject line that is personal and is elaborated on the first and second line of the email.""",  
#     }


#     prompt_template = """
#     Personalization Data:

#     {personalizationData}
#     --------
#     You are a careful, creative, and thoughtful Sales Development Representative at {myCompany}.
#     You are writing a personalization for an email to {lead_name} from {lead_company} using personalization data further referred to as PD. Here are the rules you have to follow.
#     Rules:
#     1. The output should be a json object with the following format:
#     {output_format}
#     2. The output should be kind, thoughtful, and personal, while keeping the language found in the values, not keys, of the PD or simpler.
#     3. Use only one field's value from the PD in the personalization, unless they cover the same topic, don't mention the key names of the field.
#     4. Some of the data might be site specific like cookies, privacy policy, cloudflare, etc. Do not use this data in the personalization, don't use quotations within the answer sentences.
#     5. Channel the same energy as you infer from the PD field you are referring to, meaning if the message is humorous, be humorous, if it is inspiring, be inspired, etc.
#     6. Only output the json object.
#     RESPONSE:
#     """
#     #print a populated prompt
#     return invoke_chain(model="sonnet", temperature=0.2, 
#                         prompt_template=prompt_template, output_parser="json", 
#                         data = {"personalizationData": personalizationData,
#                             "lead_name": lead.get('first_name', ""),
#                             "lead_company": lead.get('company', ""),
#                             "myCompany": client.get('company_name', ""),
#                             "output_format": output_format})

def writeTheBestBrightBoundEmail(lead, client, outputFormat = None, base_format = None):
    
    emailBaseFormat = base_format if base_format != None and base_format != "" else """
    Hi \{ firstName \},

    \{ BODY \}

    \{ Call To Action \}

    \{ Signoff \}"""
    if outputFormat == None or outputFormat == "":
        outputFormat = {
        "personalization": "Congratulations or praise based on linkedIn information and recent accomplishments.  This needs to be a standalone sentence~20 words",

        "body": "I wanted to reach out because we turn [specific description of their business mentioning their niche, subsegment, and location ~ 7 words] like yours into client magnets. On your behalf, we get you [their ICP 7~15 words] and [ICPs goals, can be found in the offer] and connect them with you directly."
        }
        
    
    prompt_template = """Company to reach out: {company}

    Send to: {name} from {company} whose background is {linkedin_summary}

    Information about {company}: {company_summary}

    ----

    You are a sales rep at {myCompany}, here is some background context:

    {product_context}

    ----

    I need to write an email that will follow the following format:

    {emailBaseFormat}

    Please help me generate the BODY of the outreach email to {name} from {company}.
    regarding the BrightBoundAI service, listing the value proposition clearly;

    Rule 1: The email body should be very personal, unique that can ONLY be said to {company}

    Rule 2: The email body should be short and straight to the point, less than 100 words.

    Rule 3: The email body should talk about what unique use cases {company} can do & benefit from BrightBoundAI.

    Rule 4: Do not mention their name in the email body.

    Rule 5: Your output should be in the json format as follows:

    {output_format}

    Rule 6: Return only the json object as the response starting and ending with curly brackets. Your output will be treated as a valid json object.
    
    RESPONSE:"""

    return invoke_chain(model="sonnet", temperature=0.2,
                        prompt_template=prompt_template, output_parser="json",
                        data = {  "product_context": client['company_summary'],
                        "myCompany": client['company_name'],
                        "company": lead['company'],
                        "name": lead['first_name'],
                        "linkedin_summary": lead['linkedin_summary'],
                        "emailBaseFormat": emailBaseFormat,
                        "output_format": outputFormat,
                        "company_summary": {
                            "summary": lead['website_summary'], 
                            "icp": lead['icp'], 
                            "offer": lead['offer']}
    })

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