import dotenv
import os
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json



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
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    return llm_chain(inputs={"text": profile})


def summarizeWebsiteContent(content, context):
    
    formatString = str({
        "client_service": "3-5 word service description",
        "client_icp": "Their ideal customer profile",
        "offer": "the services they are offering to the ICP"
    })
    
    prompt_template = """
    WEBSITE CONTENT:
    {website_content}

    Based on the information above provide me the following:

    1. Give me a 100-word summary of the above website content. I will use this summary to personalise my cold outreach to employees of this company. The summary you give me must be highly relevant to my product and service. Focus on the potential challenges and opportunities this company might face, where my product and service could potentially provide significant value.

    2. Give me a 10 word summary of the ideal customer profile that you infer from the website content, only talk about the website content in this section, not my product.

    3. Give me a 20 word summary of their offer to their ICP and the services they provide them, only talk about the website content in this section, not my product.

    CONTEXT ABOUT MY PRODUCT:

    {product_context}

    Your response MUST be in the following json format, return just the json:

    {format}

    RESPONSE:"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["website_content", "product_context", "format"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    return json.loads(llm_chain(inputs={"website_content": content, 
                             "product_context": context,
                             "format": formatString})['text'])

