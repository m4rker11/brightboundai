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