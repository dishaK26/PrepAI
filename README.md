# 🤖 PrepAI — AI Technical Interview Assistant

PrepAI is an AI-powered technical interview preparation assistant that helps users generate clear, accurate, and interview-ready answers to technical questions.

It combines a **ReAct agent** with an **iterative answer improvement loop** to generate, evaluate, critique, and refine interview answers.

---

## ✨ Features

- 🧠 **ReAct Agent** — Reason → Act → Observe → Answer
- 🔍 **Knowledge Retrieval** for technical concepts
- 🔄 **Iterative Answer Improvement**
- 📊 **AI-based Interview Evaluation**
- ⭐ **Interview Answer Scoring**
- 🎤 **Voice Question Input**
- 📝 **Automatic Speech-to-Text**
- ⚡ **FastAPI Backend**
- 🎨 **Streamlit Frontend**

---

## 🏗️ Project Architecture

```text
                         ┌────────────────────┐
                         │    Streamlit UI    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │    FastAPI API     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │    ReAct Agent     │
                         │                    │
                         │ Reason → Act →     │
                         │ Observe → Answer   │
                         └─────────┬──────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │   Answer Evaluation    │
                       │                        │
                       │ Accuracy               │
                       │ Relevance              │
                       │ Completeness           │
                       │ Clarity                │
                       │ Hallucination-free     │
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │  Improvement Loop      │
                       │                        │
                       │ Critique → Improve     │
                       └───────────┬────────────


🛠️ Tech Stack
Python
Google Gemini API
FastAPI
Streamlit
Pydantic
Requests
Uvicorn
audio-recorder-streamlit
📂 Project Structure
PrepAI/
│
├── app.py                 # ReAct agent and improvement loop
├── api.py                 # FastAPI backend
├── ui.py                  # Streamlit frontend
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
├── .gitignore             # Files excluded from Git
│
└── screenshots/
  
🚀 How to Run
1. Clone the repository
git clone <your-repository-url>
cd PrepAI
2. Create a virtual environment
python -m venv venv

Activate it on Windows:

venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure Gemini API

Set your Gemini API key as an environment variable.

Windows PowerShell:

$env:GEMINI_API_KEY="your_api_key"

Never commit your API key to GitHub.

5. Start the FastAPI backend
uvicorn api:app --reload
6. Start the Streamlit frontend

Open another terminal:

streamlit run ui.py
🎤 Voice Interview Questions

PrepAI allows users to ask questions using their microphone.

The workflow is:

🎤 Record Question
        ↓
Audio → FastAPI
        ↓
Gemini Speech-to-Text
        ↓
Transcribed Question
        ↓
ReAct Agent
        ↓
Improvement Loop
        ↓
Final Interview Answer
🔄 Answer Improvement Workflow

PrepAI doesn't simply generate an answer once.

It follows an iterative process:

Question
   ↓
ReAct Agent
   ↓
Initial Answer
   ↓
Evaluation
   ↓
Critique
   ↓
Improvement
   ↓
Quality Check
   ↓
Final Answer

The evaluator considers:

Accuracy
Relevance
Completeness
Clarity
Hallucination-free response

The process stops when the answer reaches the configured quality threshold or the maximum number of improvement iterations.

📸 Screenshots
PrepAI Interface

Voice Question

Generated Interview Answer

🎯 Purpose

PrepAI was built as a practical exploration of AI agents, tool usage, iterative evaluation, and LLM-powered interview preparation.

The project demonstrates how multiple AI components can be combined into a complete application rather than using an LLM as a simple question-answering interface.

👩‍💻 Built With ❤️ by Disha

                       │ Final Interview Answer │
                       └────────────────────────┘
