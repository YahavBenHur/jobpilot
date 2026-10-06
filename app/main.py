from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.analyzer import analyze_match
from app.config import APP_ENV
from app.cv_reader import extract_text_from_pdf
from app.schemas import MatchResult

app = FastAPI(title="JobPilot")


@app.get("/health")
def health():
    return {"status": "ok", "env": APP_ENV}


@app.post("/analyze", response_model=MatchResult)
def analyze(cv: UploadFile = File(...), job_text: str = Form(...)):
    if cv.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="CV must be a PDF file")

    cv_text = extract_text_from_pdf(cv.file.read())
    if not cv_text:
        raise HTTPException(status_code=400, detail="Could not read text from the PDF")

    return analyze_match(cv_text, job_text)