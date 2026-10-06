from fastapi import FastAPI
from app.config import APP_ENV

app = FastAPI(title="JobPilot")

@app.get("/health")
def health():
    return {"status": "ok", "env": APP_ENV}