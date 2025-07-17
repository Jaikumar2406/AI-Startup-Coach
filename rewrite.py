from typing import Annotated,Sequence, TypedDict
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


groq = os.getenv('groq')
llm = ChatGroq(api_key=groq, temperature=0.5, model="llama-3.3-70b-versatile")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
def rewrite(state:AgentState):
    messages = state["messages"]
    question = messages[0].content
    
    message = [HumanMessage(content=f"""Look at the input and try to reason about the underlying semantic intent or meaning. 
                    Here is the initial question: {question} 
                    Formulate an improved question: """)
       ]
    response = llm.invoke(message)
    return {"messages": [response]}