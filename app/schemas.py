from pydantic import BaseModel, Field


class MatchResult(BaseModel):
    summary: str = Field(
        description="2-3 sentences: what kind of role this is and how well the candidate fits it."
    )
    score: int = Field(
        description="Integer 0-100, assigned strictly according to the scoring rubric."
    )
    matching_skills: list[str] = Field(
        description="Requirements the CV clearly meets. Short phrases, max 6 words each."
    )
    missing_required: list[str] = Field(
        description="Mandatory requirements the CV does not show. Short phrases, max 6 words each."
    )
    missing_nice_to_have: list[str] = Field(
        description="Advantage/optional requirements the CV does not show. Short phrases, max 6 words each."
    )
    suggestions: list[str] = Field(
        description="Up to 5 concrete suggestions for presenting the candidate's REAL experience better. One sentence each."
    )