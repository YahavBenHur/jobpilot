from pydantic import BaseModel


class MatchResult(BaseModel):
    score: int                   # ציון התאמה 0-100
    summary: str                 # סיכום קצר
    matching_skills: list[str]   # כישורים שמתאימים למשרה
    missing_skills: list[str]    # דרישות שחסרות בקורות החיים
    suggestions: list[str]       # המלצות לשיפור, בלי להמציא ניסיון