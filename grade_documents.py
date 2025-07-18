from typing import Annotated,Literal, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.pydantic_v1 import BaseModel, Field

load_dotenv()


groq = os.getenv('GROQ')
llm = ChatGroq(api_key=groq, temperature=0.5, model="llama-3.3-70b-versatile")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class grade(BaseModel):
    binary_score:str=Field(description="Relevance score 'yes' or 'no'")

def grade_documents(state:AgentState)->Literal["Output_Generator", "Query_Rewriter"]:
    llm_with_structure_op=llm.with_structured_output(grade)
    
    prompt=PromptTemplate(
        template="""You are a grader deciding if a document is relevant to a user’s question.
                    Here is the document: {context}
                    Here is the user’s question: {question}
                    If the document talks about or contains information related to the user’s question, mark it as relevant. 
                    Give a 'yes' or 'no' answer to show if the document is relevant to the question.""",
                    input_variables=["context", "question"]
                    )
    chain = prompt | llm_with_structure_op
    
    messages = state["messages"]
    last_message = messages[-1]
    question = messages[0].content
    docs = last_message.content
    scored_result = chain.invoke({"question": question, "context": docs})
    score = scored_result.binary_score

    if score == "yes":
        return "generator" 
    else:
        return "rewriter" 
