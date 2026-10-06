import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")