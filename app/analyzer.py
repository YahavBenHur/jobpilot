from anthropic import Anthropic

from app.config import LLM_API_KEY, LLM_MODEL
from app.prompts import build_system_prompt
from app.schemas import MatchResult


def get_client() -> Anthropic:
    if not LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is missing. Add it to your .env file.")
    return Anthropic(api_key=LLM_API_KEY)


def analyze_match(cv_text: str, job_text: str, language: str = "he") -> MatchResult:
    client = get_client()
    response = client.messages.parse(
        model=LLM_MODEL,
        max_tokens=2048,
        system=build_system_prompt(language),
        messages=[
            {
                "role": "user",
                "content": f"<cv>\n{cv_text}\n</cv>\n\n<job_posting>\n{job_text}\n</job_posting>",
            }
        ],
        output_format=MatchResult,
    )
    return response.parsed_output