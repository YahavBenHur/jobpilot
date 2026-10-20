import json

from app import storage
from app.analyzer import analyze_match

STATUSES = ["interested", "applied", "interview", "rejected", "offer"]

TOOLS = [
    {
        "name": "analyze_job",
        "description": (
            "Analyzes how well the user's saved CV matches a job posting. "
            "Returns a match score (0-100), a summary, matching skills, missing required "
            "and nice-to-have skills, and suggestions. Use it whenever the user shares a job "
            "posting or asks how well they fit a job. It requires a CV to be uploaded first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_text": {
                    "type": "string",
                    "description": "The full text of the job posting, exactly as the user provided it.",
                }
            },
            "required": ["job_text"],
        },
    },
    {
        "name": "save_application",
        "description": (
            "Saves a job application to the user's tracking list. Use it when the user asks to "
            "save, track or remember a job. Requires the company name and the job title. "
            "If an analysis was done in this conversation, include its score."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "company": {"type": "string", "description": "The company name."},
                "title": {"type": "string", "description": "The job title."},
                "score": {"type": "integer", "description": "Match score from analyze_job, if available."},
                "status": {
                    "type": "string",
                    "enum": STATUSES,
                    "description": "The current status of the application. If the user did not say, use 'interested'.",
                },
            },
            "required": ["company", "title"],
        },
    },
    {
        "name": "list_applications",
        "description": (
            "Returns the user's saved job applications, optionally filtered by status. "
            "Use it when the user asks about jobs they saved, applied to or are tracking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": STATUSES,
                    "description": "Optional filter by status.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "update_application_status",
        "description": (
            "Updates the status of an existing saved application. Use it when the user says "
            "they applied, got an interview, were rejected or got an offer for a job they saved. "
            "It needs the application id: if you do not know it, call list_applications first "
            "and find the matching application by company and title."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {
                    "type": "integer",
                    "description": "The id of the application, from list_applications.",
                },
                "status": {
                    "type": "string",
                    "enum": STATUSES,
                    "description": "The new status.",
                },
            },
            "required": ["application_id", "status"],
        },
    },
]


def run_tool(name: str, tool_input: dict, language: str) -> str:
    if name == "analyze_job":
        cv_text = storage.load_cv()
        if not cv_text:
            raise ValueError("No CV has been uploaded yet. The user must upload a CV first.")
        result = analyze_match(cv_text, tool_input["job_text"], language)
        return result.model_dump_json()

    if name == "save_application":
        saved = storage.save_application(
            company=tool_input["company"],
            title=tool_input["title"],
            score=tool_input.get("score"),
            status=tool_input.get("status", "interested"),
        )
        return json.dumps(saved, ensure_ascii=False)

    if name == "list_applications":
        applications = storage.list_applications(tool_input.get("status"))
        return json.dumps(applications, ensure_ascii=False)

    if name == "update_application_status":
        updated = storage.update_application_status(
            application_id=tool_input["application_id"],
            status=tool_input["status"],
        )
        return json.dumps(updated, ensure_ascii=False)

    raise ValueError(f"Unknown tool: {name}")