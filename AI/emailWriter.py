import dotenv
import os
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser

from langchain_core.output_parsers import StrOutputParser
dotenv.load_dotenv()
# llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.1, model_name="gpt-4-1106-preview")

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
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0.2)
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser
    return chain.invoke({  
        "product_context": client['company_summary'],
        "myCompany": client['company_name'],
        "company": lead['company'],
        "name": lead['first_name'],
        "linkedin_summary": lead['linkedin_summary'],
        "emailBaseFormat": emailBaseFormat,
        "output_format": outputFormat,
        "company_summary": {"summary": lead['website_summary'], "icp": lead['icp'], "offer": lead['offer']}
    })

def emailTemplateWriterForLead(lead):
    email = """
    Subject: Celebrating Your Success and Learning from Others

    Hi {{Your past client's first name}},

    Time flies! It’s been {{months since last purchase}} months since you started using {companyName}'s services. 
    I hope it's been great for {{your past client's company name}}.

    I wanted to share a quick story. One of our clients, {{another client’s company}}, was in a similar spot as you. 
    With our help, they managed to {{key achievement you helped them with}}. I think there’s a chance for {{your past client's company name}} to have the same success.

    What do you think about a quick call to talk about it and see how we can help you even more?

    Cheers,
    {firstName}

    """
    return email.format(companyName=lead['company'], firstName=lead['first_name'])



def writeEmailFieldsFromCampaignAndLeadInfoFromFormat(email_templates, client_context, lead, model = "gpt4") -> dict:
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
    7. Ignore and disregard fields called "accountSignature" and "emailTemplate". They should not be present in the output.
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
    model_name = "gpt-4-1106-preview" if model == "gpt4" else "gpt-3.5-turbo-1106"
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model_name=model_name, temperature=0.1)
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser
    return chain.invoke({"email_templates": email_templates,
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
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0.1)
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser
    return chain.invoke({"emails": campaign,
                            "lead_info": lead,
                            "client_context": client_context,
                            "lead_name": lead['first_name'],
                            "lead_company": lead['company']})