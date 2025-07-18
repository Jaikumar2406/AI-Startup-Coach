from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os
from ai_assistant import ai_assistant
from ask_question import ask_question
from generate import generate
from retriever_tool import retriever_tool
from rewrite import rewrite
from grade_documents import grade_documents


app = FastAPI()

load_dotenv()


class InputText(BaseModel):
    input: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pine_cone = os.getenv('PINE_CONE')
groq = os.getenv('GROQ')
hugging_face = os.getenv("HUGGING_FACE")
host_bg = os.getenv('HOST_BG') 

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

llm = ChatGroq(api_key=groq, temperature=0.5, model="llama-3.3-70b-versatile")
tools = [ask_question ,retriever_tool ]                    
retrieve=ToolNode(tools) 
  
workflow=StateGraph(AgentState)
workflow.add_node("My_Ai_Assistant",ai_assistant)
workflow.add_node("Vector_Retriever", retrieve) 
workflow.add_node("Output_Generator", generate)
workflow.add_node("Query_Rewriter", rewrite)

workflow.add_edge(START,"My_Ai_Assistant")
workflow.add_conditional_edges("My_Ai_Assistant",
                               
                            tools_condition,
                            {"tools": "Vector_Retriever",
                                END: END,})
workflow.add_conditional_edges("Vector_Retriever",
                            grade_documents,
                            {"generator": "Output_Generator",
                            "rewriter": "Query_Rewriter",
                            }
                            )
workflow.add_edge("Output_Generator", END)
workflow.add_edge("Query_Rewriter", "My_Ai_Assistant")
workflowrun = workflow.compile()




@app.get("/")
def root():
    return {"message": "Agent system is running"}

@app.post("/generate")
async def generate_text(data: InputText):
    user_input = data.input.strip()

    if user_input.lower() in {"exit", "quit", "stop"}:
        return {"answer": "Session ended."}

    try:
        result = await workflowrun.ainvoke({"messages": [HumanMessage(content=user_input)]})
        last_msg = result["messages"][-1]

        if isinstance(last_msg, AIMessage) and last_msg.content:
            return {"answer": last_msg.content}
        else:
            return {"answer": "I'm processing your request..."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))