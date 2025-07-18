import os
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain.tools.retriever import create_retriever_tool

load_dotenv()

pine_cone = os.getenv('PINE_CONE')
groq = os.getenv('GROQ')
hugging_face = os.getenv("HUGGING_FACE")
host_bg = os.getenv('HOST_BG') 

llm = ChatGroq(api_key=groq, temperature=0.5, model="llama-3.3-70b-versatile")
embedding = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5", model_kwargs={"token": hugging_face})

pc = Pinecone(api_key=pine_cone)
index = pc.Index("teacher", host=host_bg)
vector = PineconeVectorStore(index=index, embedding=embedding, text_key="page_content")
retriever = vector.as_retriever()


def retriever_tool():
    """Tool for retrieving information about startup coaching, VCs, and MVPs."""
    retriever_tool_instance = create_retriever_tool(
        retriever,
        "startup_coach_retriever",
        "Search and return helpful information about startup coaching, how people gro their startup even there small ideas. Use this only when the query is about startup building, fundraising, or entrepreneurship."
    )
    return retriever_tool_instance

