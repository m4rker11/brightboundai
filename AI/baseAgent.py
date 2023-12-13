from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser, JSONAgentOutputParser
from langchain.tools.render import render_text_description
from langchain.agents import AgentExecutor
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents.format_scratchpad import format_to_openai_function_messages

def run_json_agent(prompt):

    llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo-1106")
    agent = (
    {
        "input": lambda x: x["input"],
        # Format agent scratchpad from intermediate steps
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm
    | JSONAgentOutputParser()
    )
    memory = ConversationBufferMemory(memory_key="chat_history")
    agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True, handle_parsing_errors=True)   
    return agent_executor.invoke({"input": prompt})["output"]