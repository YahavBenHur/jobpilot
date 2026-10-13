import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
CV_FILE = DATA_DIR / "cv.txt"
APPLICATIONS_FILE = DATA_DIR / "applications.json"


def save_cv(text: str) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    CV_FILE.write_text(text, encoding="utf-8")


def load_cv() -> str | None:
    if not CV_FILE.exists():
        return None
    return CV_FILE.read_text(encoding="utf-8")


def _load_applications() -> list[dict]:
    if not APPLICATIONS_FILE.exists():
        return []
    return json.loads(APPLICATIONS_FILE.read_text(encoding="utf-8"))


def save_application(company: str, title: str, score: int | None, status: str) -> dict:
    applications = _load_applications()
    application = {
        "id": len(applications) + 1,
        "company": company,
        "title": title,
        "score": score,
        "status": status,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    applications.append(application)
    DATA_DIR.mkdir(exist_ok=True)
    APPLICATIONS_FILE.write_text(
        json.dumps(applications, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return application


def list_applications(status: str | None = None) -> list[dict]:
    applications = _load_applications()
    if status:
        applications = [a for a in applications if a["status"] == status]
    return applications