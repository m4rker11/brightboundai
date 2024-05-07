import dotenv
import os
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json



dotenv.load_dotenv()
llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], temperature=0.1, model_name="gpt-3.5-turbo-1106")


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

