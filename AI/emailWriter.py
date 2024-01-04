import dotenv
import os
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers.json import SimpleJsonOutputParser
dotenv.load_dotenv()
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.1, model_name="gpt-4-1106-preview")

def writeEmailFromFormat(name,base_format, company, linkedin_summary, product_context, outputFormat):
    
    emailBaseFormat = base_format if base_format != None and base_format != "" else """
    Hi \{ firstName \},

    \{ BODY \}

    \{ Call To Action \}

    \{ Signoff \}"""
    if outputFormat == None or outputFormat == "":
        outputFormat = {
        "personalization": "Congratulations or praise based on linkedIn information and recent accomplishments.  This needs to be a standalone sentence~20 words",

        "body": "I wanted to reach out because we connect [specific description of their business mentioning their niche, subsegment, and location ~ 7 words] like yours with [their ICP ~15 words] and [ICPs goals, can be found in the offer]."
        }
        
    
    prompt_template = """Company to reach out: {company}

    Send to: {name} from {company} whose background is {linkedin_summary}

    ----

    Here is the context about the product you are trying to sell:

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
    model = ChatOpenAI()
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser
    return chain.invoke({  
        "product_context": product_context,
        "company": company,
        "name": name,
        "linkedin_summary": linkedin_summary,
        "emailBaseFormat": emailBaseFormat,
        "output_format": outputFormat
    })

def generateEmailFormat(product_context, target, email_objective):
    
    json_format = """
    {{
    "campaign": text, //this is what the email will look like aka "Dear {{ firstName }}, {{ body }}, {{ callToAction }}, {{ signoff }}"
    "variables": dict, //this is the dictionary of variables that will be used to fill in the campaign, aka {{"firstName": "John", "body": "I wanted to reach out because we connect [specific description of their business mentioning their niche, subsegment, and location ~ 7 words] like yours with [their ICP ~15 words] and [ICPs goals, can be found in the offer].", "callToAction": "I would love to chat with you about how we can help you achieve your goals.  Are you available for a quick call this week?"}}
    }}
    """
    
    prompt_template = """ 
    You are crafting an email template that is sure to appeal to the following ICP: 
    ---
    {target}
    
    Every field in the ICP above is known for each client who fits this ICP.
    ---
    
    You want to sell them the following product:
    ---
    {product_context}
    ---
    In order to do that you want to create a campaign template
    that can be used by other to create an appealing and personalized email.
    This template will be fed to an LLM along with information about a specific client to turn this template into a personalized email.
    ---
    {injection}
    ---
    The template should follow the following json format:
    ---
    {json_format}

    When this template will be used for personalized email, personalization will occur to what is within the square brackets[]. 
    What is not surrounded by square brackets will end up in the email as is.    
    """.format(injection=email_objective, json_format=json_format, target=target, product_context=product_context)    
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', "You are a professional Sales Development Representative (SDR) at BrightBoundAI."),
            ('user', prompt_template)
        ]
    )
    chain = prompt | llm | SimpleJsonOutputParser()
    return chain.invoke({"input": prompt_template})

    

def generateSummaryOutput(profile_summary, website_summary):
    prompt_template = """
    PROFILE SUMMARY:
    {profile_summary}

    WEBSITE SUMMARY:
    {website_summary}

    Based on the information above, provide concise key-value pairs for each of the following in a JSON format:
    1. whatTheyDo: What the company does (3-6 words)
    2. theirCustomers: Who are their customers (3-6 words)
    3. theirGoals: What are their goals (3-6 words)
    4. theirCustomersGoals: What their customers are looking to accomplish (3-6 words)
    5. theirOffer: Their offer to their customers (3-6 words)
    6. painPoints: What are their pain points (3-6 words)
    7. Background: Their background (3-6 words)
    8. Expertise: What they are experts in (3-6 words)
    9. Role: What is their role at the company (3-6 words)
    10. Location: Where they are based in (3-6 words)

    Your response must be a valid JSON object

    RESPONSE:"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI()
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser

    result = chain.invoke({"profile_summary": profile_summary, "website_summary": website_summary})
    return json.loads(result)

def writeEmailFieldsFromCampaignAndLeadInfoFromFormat(email_templates,client_context, lead) -> dict:
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
    1. The keys in the json object must be the same as the fields from the email templates shown as {{ }} in the email templates.
    2. The values in the json object must be the personalized information from the lead.
    3. When the values are plugged in to the email templates, the resulting emails should be the final personalized email to the lead.
    4. The emails are written with the goal of bringing the lead in for a conversation with the client, the description of the client is in the client context.
    5. When the values are plugged in to the email templates, the resulting emails should be coherent and sound human.
    6. Output only the json object as the response starting and ending with curly brackets. Your output will be treated as a valid json object.
    
    OUTPUT:
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model_name="gpt-4-1106-preview")
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser
    return chain.invoke({"email_templates": email_templates,
                            "lead_info": lead,
                            "client_context": client_context,
                            "lead_name": lead['name'],
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
        c. The email should not make any assumptions and rely only on the lead information and the client context.
        d. The email should be under 130 words.
        e. There should be no random capitalization.
    5. The list should be in the same order as the emails in the sequence and of the same length.
    6. The emails are written with the goal of bringing the lead in for a conversation with the client, the description of the client is in the client context.

    OUTPUT:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model_name="gpt-4-1106-preview")
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser
    return chain.invoke({"emails": campaign['emails'],
                            "lead_info": lead,
                            "client_context": client_context,
                            "lead_name": lead['name'],
                            "lead_company": lead['company']})