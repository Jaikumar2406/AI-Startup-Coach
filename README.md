readme_content = """
# 🚀 AI Startup Coach

An intelligent startup advisor web app designed to provide real-time, book-based advice to entrepreneurs using Retrieval-Augmented Generation (RAG) and LLMs like Groq's LLaMA-3.

---

## 🧠 What It Does

AI Startup Coach helps startup founders:
- Understand & solve startup/business-related challenges
- Get strategy insights from top entrepreneurship books
- Maintain memory across conversations (session-based)
- Chat via a web UI
- (Optional) Speak answers using Text-to-Speech (TTS)

---

## 📦 Tech Stack

| Layer        | Tool/Library                            |
|--------------|-----------------------------------------|
| 🧠 LLM        | [Groq](https://groq.com/) + LangChain   |
| 📚 RAG        | LangChain + Pinecone                    |
| 🎙️ TTS       | gTTS (Google TTS)        |
| 🌐 Backend   | FastAPI                                 |
| 💻 Frontend  | JS + HTML/CSS                   |

---

## .env file
groq=your_groq_api_key
pine_cone=your_pinecone_key
host_bg=https://your-pinecone-host-url
hugging_face=your_huggingface_token

