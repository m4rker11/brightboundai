import dotenv
import os
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.schema.output_parser import StrOutputParser
dotenv.load_dotenv()

def summarizeProfileData(profile):
    prompt_template = """

    {text}

    ---

    This is the linkedin profile of a potential prospect, summarise this person's profile and posts. 
    Focus on recent events, accomplishments or specifics, and highlight 3 of them in the summary. 
    This will be used for personalizing a cold email.
    Use no more than 200 words.
    Your output should be a json with two fields: "profile summary" and "posts summary".
    If either is missing, return "Not applicable" for that field.
    CONCISE SUMMARY JSON:"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model="gpt-3.5-turbo-1106")
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser

    return tryThrice(chain, {"text": profile})


def summarizeWebsiteContent(content, context):
        
        formatString1 = str({
        "summary": "targeted summary relevant to my product",
        "icp": "Their ideal customer profile",
        "offer": "the services they are offering to the ICP"
        })
        
        prompt_template1 = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information above provide me the following:
    
        1. Give me a 150-word summary of the above website content. I will use this summary to personalise my cold outreach to employees of this company. Focus on the potential challenges and opportunities this company might face.
    
        2. Give me a 10 word summary of the ideal customer profile that you infer from the website content. This ICP summary needs to start with either the word "Businesses" if the company is B2B or "Individuals" if the company is B2C. 
    
        3. Give me a 20 word summary of their offer to their ICP and the services they provide them.
    
        CONTEXT ABOUT MY PRODUCT:
    
        {product_context}
    
        Your response MUST be in the following json format, return just the json:
    
        {format}
    
        RESPONSE:"""
        prompt1 = ChatPromptTemplate.from_template(prompt_template1)
        model = ChatOpenAI(model="gpt-3.5-turbo-1106")
        output_parser = SimpleJsonOutputParser()
    
        chain = prompt1 | model | output_parser
        input = {"website_content": content, "product_context": context, "format": formatString1}
        return tryThrice(chain, input)

def tryThrice(chain, input):
    result = None
    for i in range(2):
        if result is None:
            result = chain.invoke(input)
        else:
            break
    return result


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