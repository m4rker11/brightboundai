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
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.1, model_name="gpt-3.5-turbo-1106")



def summarizeProfileData(profile):
    prompt_template = """

    {text}

    ---

    This is the linkedin profile of a potential prospect, summarise this person's profile and posts. 
    Focus on recent events, accomplishments or specifics, and highlight 3 of them in the summary. 
    This will be used for personalizing a cold email.
    Use no more than 200 words.

    CONCISE SUMMARY:"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI()
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser

    return chain.invoke({"text": profile})



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
    
        1. Give me a 150-word summary of the above website content. I will use this summary to personalise my cold outreach to employees of this company. Focus on the potential challenges and opportunities this company might face, where my product and service could potentially provide significant value.
    
        2. Give me a 10 word summary of the ideal customer profile that you infer from the website content.
    
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
        
        return chain.invoke({"website_content": content, 
                                "product_context": context,
                                "format": formatString1})

