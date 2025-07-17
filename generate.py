from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
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

def generate(state:AgentState):
    messages = state["messages"]

    question = messages[0].content
    
    last_message = messages[-1]
    docs = last_message.content
    
    prompt = PromptTemplate(
    template="You are a helpful assistant. Use the following context to answer the user's question.\n\nContext:\n{context}\n\nQuestion: {question}",
    input_variables=["context", "question"]
)
    
    rag_chain = prompt | llm

    response = rag_chain.invoke({"context": docs, "question": question})
    return {"messages": [response]}