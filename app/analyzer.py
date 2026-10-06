from anthropic import Anthropic

from app.config import LLM_API_KEY, LLM_MODEL
from app.schemas import MatchResult

SYSTEM_PROMPT = """You are an experienced tech recruiter and career advisor.
You compare a candidate's CV with a job posting and assess how well they match.

Rules:
- Base your analysis ONLY on what is written in the CV. Never assume skills or experience that are not stated.
- Suggestions must help the candidate present their REAL experience better. Never suggest adding experience they do not have.
- The score is an integer from 0 to 100, where 100 means the CV meets every requirement.
- Be specific and honest, including about gaps."""


def get_client() -> Anthropic:
    if not LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is missing. Add it to your .env file.")
    return Anthropic(api_key=LLM_API_KEY)


def analyze_match(cv_text: str, job_text: str) -> MatchResult:
    client = get_client()
    response = client.messages.parse(
        model=LLM_MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"<cv>\n{cv_text}\n</cv>\n\n<job_posting>\n{job_text}\n</job_posting>",
            }
        ],
        output_format=MatchResult,
    )
    return response.parsed_output