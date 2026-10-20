import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
CV_FILE = DATA_DIR / "cv.txt"
APPLICATIONS_FILE = DATA_DIR / "applications.json"
CONVERSATIONS_DIR = DATA_DIR / "conversations"


# ---------- CV ----------

def save_cv(text: str) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    CV_FILE.write_text(text, encoding="utf-8")


def load_cv() -> str | None:
    if not CV_FILE.exists():
        return None
    return CV_FILE.read_text(encoding="utf-8")


# ---------- Applications ----------

def _load_applications() -> list[dict]:
    if not APPLICATIONS_FILE.exists():
        return []
    return json.loads(APPLICATIONS_FILE.read_text(encoding="utf-8"))


def _save_applications(applications: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    APPLICATIONS_FILE.write_text(
        json.dumps(applications, ensure_ascii=False, indent=2), encoding="utf-8"
    )


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
    _save_applications(applications)
    return application


def list_applications(status: str | None = None) -> list[dict]:
    applications = _load_applications()
    if status:
        applications = [a for a in applications if a["status"] == status]
    return applications


def update_application_status(application_id: int, status: str) -> dict:
    applications = _load_applications()
    for application in applications:
        if application["id"] == application_id:
            application["status"] = status
            application["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save_applications(applications)
            return application
    raise ValueError(f"No application found with id {application_id}")


# ---------- Conversations ----------

def is_valid_conversation_id(conversation_id: str) -> bool:
    try:
        uuid.UUID(conversation_id)
        return True
    except ValueError:
        return False


def load_conversation(conversation_id: str) -> list[dict]:
    path = CONVERSATIONS_DIR / f"{conversation_id}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_conversation(conversation_id: str, messages: list[dict]) -> None:
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = CONVERSATIONS_DIR / f"{conversation_id}.json"
    path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")