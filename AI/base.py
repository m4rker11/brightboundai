from langchain.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers.boolean import BooleanOutputParser
import dotenv
import os
dotenv.load_dotenv()
openai_api_key=os.environ["OPENAI_API_KEY"]
claude_api_key=os.environ["ANTHROPIC_API_KEY"]


def invoke_chain(model, temperature, prompt_template, output_parser, data, retry=3):
    prompt = ChatPromptTemplate.from_template(prompt_template)

    if model == "gpt-3.5":
        model = ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature, openai_api_key=openai_api_key)
    elif model == "gpt-4":
        model = ChatOpenAI(model="gpt-4-turbo-preview", temperature=temperature, openai_api_key=openai_api_key)
    elif model == "haiku":
        model = ChatAnthropic(temperature=temperature, anthropic_api_key=claude_api_key, model_name="claude-3-haiku-20240307")
    elif model == "sonnet":
        model = ChatAnthropic(temperature=temperature, anthropic_api_key=claude_api_key, model_name="claude-3-sonnet-20240229")
    
    if output_parser == "json":
        output_parser = SimpleJsonOutputParser()
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
