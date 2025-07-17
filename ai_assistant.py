from typing import Annotated, Literal, Sequence, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import PromptTemplate
from ask_question import ask_question
from retriever_tool import retriever_tool
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


groq = os.getenv('groq')
llm = ChatGroq(api_key=groq, temperature=0.5, model="llama-3.3-70b-versatile")

tools = [ask_question ,retriever_tool ]   
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
def ai_assistant(state: AgentState):
    messages = state["messages"]
    question = messages[-1].content  

    llm_with_tool = llm.bind_tools(tools)

    prompt = PromptTemplate(
        template="""You are a helpful assistant.
If the message is a greeting like 'hi', 'hell, or 'hey', just greet back nicely.
If the question is about startups/business, call 'retriever_tool'.
If it's about hackathons, call 'ask_question'.
Otherwise say "Sorry, I don't know the answer to that."
If the user tells you their name, email , about there atsrtups, respond politely and remember it.
take examples is user did'nt understand and your answer should be in 0 to 500 words according to questions.

Question: {question}""",
        input_variables=["question"]
    )
    chain = prompt | llm_with_tool
    response = chain.invoke({"question": question})
    return {"messages": [response]}