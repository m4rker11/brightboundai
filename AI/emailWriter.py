import dotenv
import os
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers.json import SimpleJsonOutputParser
dotenv.load_dotenv()
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.1, model_name="gpt-4-1106-preview")

def writeEmail(name, company, linkedin_summary, website_content, product_context, outputFormat):
    
    emailBaseFormat = """
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

    Value prop: {website_content}

    ----

    You are the sales rep from BrightBoundAI, 
    an AI personalization focused lead generation company that specializes 
    at targeted and performance priced cold outreach. 
    BrightBoundAI uses AI personalization to create and manage 
    successful cold email campaigns on behalf of our clients. 
    We find them prospective customers, enrich their information, then use AI to create custom 
    email campaigns for each prospect, and then deliver them on client's behalf, scheduling an 
    introductory call with the qualified prospect directly in the client's calendar. 
    Our offer is performance based, only pay for qualified prospects that show up to the call. 
    We also offer 100% money back 30 day satisfaction guarantee.

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
        "website_content": website_content,
        "product_context": product_context,
        "company": company,
        "name": name,
        "linkedin_summary": linkedin_summary,
        "emailBaseFormat": emailBaseFormat,
        "output_format": outputFormat
    })
    

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

    RESPONSE:"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI()
    output_parser = SimpleJsonOutputParser()

    chain = prompt | model | output_parser

    return chain.invoke({"profile_summary": profile_summary, "website_summary": website_summary})

