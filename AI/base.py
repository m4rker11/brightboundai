from langchain_openai import ChatOpenAI

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers.boolean import BooleanOutputParser
import os
openai_api_key=os.environ["OPENAI_API_KEY"]


def invoke_chain(model, temperature, prompt_template, output_parser, data, retry=3):
    prompt = ChatPromptTemplate.from_template(prompt_template)

    if model == "gpt-3.5":
        model = ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature, openai_api_key=openai_api_key)
    elif model == "gpt-4":
        model = ChatOpenAI(model="gpt-4o", temperature=temperature, openai_api_key=openai_api_key)
    
    if output_parser == "json":
        output_parser = JsonOutputParser()
    elif output_parser == "str":
        output_parser = StrOutputParser()
    elif output_parser == "bool":
        output_parser = BooleanOutputParser()

    chain = prompt | model | output_parser
    while retry > 0:
        try:
            return chain.invoke(data)
        except:
            retry -= 1
