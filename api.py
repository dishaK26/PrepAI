from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from google.genai import types

from app import run_complete_agent, client, MODEL


app = FastAPI(title="PrepAI API")


class Query(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "PrepAI API is running!"
    }


@app.post("/solve")
def solve(query: Query):

    result = run_complete_agent(query.question)

    return {
        "question": query.question,
        "answer": result["final_answer"],
        "score": result["final_score"],
        "iterations": result["iterations"]
    }


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):

    print("\n🎙️ TRANSCRIPTION REQUEST RECEIVED")

    audio_data = await file.read()

    print(f"Audio size: {len(audio_data)} bytes")
    print(f"Audio type: {file.content_type}")

    audio_part = types.Part.from_bytes(
        data=audio_data,
        mime_type=file.content_type or "audio/wav"
    )

    print("📤 Sending audio to Gemini...")

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            "Transcribe the following audio exactly into text. "
            "Return only the spoken text.",
            audio_part
        ]
    )

    text = response.text.strip()

    print("✅ Gemini transcription completed")
    print(f"📝 Transcription: {text}")

    return {
        "text": text
    }