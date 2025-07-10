from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# ------------------- SETUP -------------------

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

# ------------------- ENV VARS -------------------

pine_cone = os.getenv('pine_cone')
groq = os.getenv('groq')
hugging_face = os.getenv("hugging_face")
host_bg = os.getenv('host_bg') 

# ------------------- MODEL + EMBEDDING -------------------

model = ChatGroq(api_key=groq, temperature=0.5, model="llama-3.3-70b-versatile")
embedding = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5", model_kwargs={"token": hugging_face})

# ------------------- PINECONE -------------------

pc = Pinecone(api_key=pine_cone)
index = pc.Index("teacher", host=host_bg)
vector = PineconeVectorStore(index=index, embedding=embedding, text_key="page_content")

# ------------------- RETRIEVER -------------------

retriver_prompt = (
    "Given a chat history and the latest user question which might reference context in the chat history,"
    "formulate a standalone question which can be understood without the chat history."
    "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
)

retriever = vector.as_retriever(search_kwargs={"k": 3})

contextual_qa = ChatPromptTemplate.from_messages([
    ("system", retriver_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

history = create_history_aware_retriever(model, retriever, contextual_qa)

# ------------------- QA PROMPT -------------------

BOT = """You are an AI Startup Coach, specifically designed to guide entrepreneurs during tough startup situations using wisdom from top entrepreneurship books.

Whenever a user shares a startup problem (e.g., failure, funding stress, team issues, growth confusion, burnout), follow this structure strictly:

1. Carefully understand the user’s problem.
2. Identify if it is truly **startup/business-related**.
   - If NOT, politely decline:  
     "I'm designed to help with startup challenges. Please ask a question related to your startup journey."
     if necessary then refer the book and author name otherwise don't take book name and author name only generate relevant query

Make sure:
- You **do NOT hallucinate** fake answers.
- If no book supports the answer, say:  
  “This isn’t directly covered in my book knowledge, but based on similar principles, here’s a possible direction…”
- Keep answers short, focused, and strategic. No storytelling unless highly relevant.

CONTEXT:
{context}

QUESTION: {input}

YOUR ANSWER:
"""

qa_bot = ChatPromptTemplate.from_messages([
    ("system", BOT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

question_answer_chain = create_stuff_documents_chain(model, qa_bot)
chain = create_retrieval_chain(history, question_answer_chain)

# ------------------- MEMORY HANDLING -------------------

store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chat_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# ------------------- ROUTES -------------------

@app.get("/")
def root():
    return {"message": "RAG system is running"}

@app.post("/generate")
def generate_text(data: InputText):
    user_input = data.input

    try:
        if user_input.lower() in ["exit", "quit", "stop"]:
            return JSONResponse(content={"answer": "Session ended."})

        response = chat_with_memory.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "143"}},
        )

        answer = response.get("answer", "Sorry, I couldn't understand that.")
        return {"answer": answer}

    except Exception as e:
        print("ERROR:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
