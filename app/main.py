from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.analyzer import analyze_match
from app.config import APP_ENV
from app.cv_reader import extract_text_from_pdf
from app.schemas import MatchResult
from typing import Literal
from app import storage
from app.agent import run_agent
from app.schemas import AgentRequest, AgentResponse, MatchResult
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

app = FastAPI(title="JobPilot")


@app.get("/health")
def health():
    return {"status": "ok", "env": APP_ENV}


@app.post("/analyze", response_model=MatchResult)
def analyze(
    cv: UploadFile = File(...),
    job_text: str = Form(...),
    language: Literal["he", "en"] = Form("he"),
):
    if cv.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="CV must be a PDF file")

    cv_text = extract_text_from_pdf(cv.file.read())
    if not cv_text:
        raise HTTPException(status_code=400, detail="Could not read text from the PDF")

    return analyze_match(cv_text, job_text, language)

@app.post("/cv")
def upload_cv(cv: UploadFile = File(...)):
    if cv.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="CV must be a PDF file")

    cv_text = extract_text_from_pdf(cv.file.read())
    if not cv_text:
        raise HTTPException(status_code=400, detail="Could not read text from the PDF")

    storage.save_cv(cv_text)
    return {"status": "saved", "characters": len(cv_text)}


@app.post("/agent", response_model=AgentResponse)
def agent(
    message: str = Form(...),
    language: Literal["he", "en"] = Form("he"),
    conversation_id: str | None = Form(None),
):
    if not conversation_id:
        conversation_id = None
    elif not storage.is_valid_conversation_id(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    answer, steps, conversation_id = run_agent(message, language, conversation_id)
    return AgentResponse(answer=answer, steps=steps, conversation_id=conversation_id)