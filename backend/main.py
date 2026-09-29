from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from backend.services.hindsight_service import HindsightService

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")
database_url = os.getenv("DATABASE_URL", "sqlite:///./backend/teammento.db")
DB_PATH = BASE_DIR / "teammento.db"
if database_url.startswith("sqlite:///"):
    sqlite_path = database_url.replace("sqlite:///", "", 1)
    DB_PATH = (BASE_DIR.parent / sqlite_path.replace("./", "")).resolve()

DEFAULT_TASK_TITLE = "Build an Employee Registration REST API using FastAPI"
DEFAULT_STEPS = [
    "Create employee model",
    "Configure database",
    "Create POST endpoint",
    "Add validation",
    "Connect API to database",
    "Test API",
]
DEFAULT_QUESTION = "I don't understand how the API connects to the database."
DEFAULT_AI_EXPLANATION = (
    "The FastAPI endpoint receives employee data, opens a database session, "
    "creates an Employee object, and commits it to SQLite through SQLAlchemy."
)

app = FastAPI(title="TeamMento AI Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hindsight = HindsightService()


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept TEXT NOT NULL,
            employee_level TEXT NOT NULL,
            task TEXT NOT NULL,
            problem TEXT NOT NULL,
            ai_explanation TEXT NOT NULL,
            mentor_explanation TEXT NOT NULL,
            successful_explanation TEXT NOT NULL,
            outcome TEXT NOT NULL,
            technologies TEXT NOT NULL,
            useful_analogy TEXT,
            failed_approach TEXT,
            successful_approach TEXT,
            used_to_help_employee TEXT,
            source TEXT NOT NULL,
            hindsight_id TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS demo_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def seed_experiences() -> None:
    demo_experiences = [
        {
            "concept": "API to Database Flow",
            "employee_level": "Fresher",
            "task": "Employee Registration REST API",
            "problem": "Fresher struggled to understand API to database connection.",
            "ai_explanation": "Technical flow with request handlers and SQLAlchemy session.",
            "mentor_explanation": "Think of API as receptionist and database layer as record room.",
            "successful_explanation": "Receptionist analogy",
            "outcome": "Successfully understood",
            "technologies": "FastAPI, SQLAlchemy, SQLite",
            "useful_analogy": "Receptionist",
            "failed_approach": "Pure technical explanation",
            "successful_approach": "Beginner analogy mapped to API flow",
            "used_to_help_employee": "Employee B",
            "source": "seed_demo",
        },
        {
            "concept": "JWT Authentication",
            "employee_level": "Junior",
            "task": "Secure login endpoint",
            "problem": "Token validation order confusion",
            "ai_explanation": "Detailed token parsing steps",
            "mentor_explanation": "Treat JWT like office entry pass checked before room access.",
            "successful_explanation": "Office pass analogy",
            "outcome": "Understood after mentor intervention",
            "technologies": "FastAPI, JWT",
            "useful_analogy": "Office entry pass",
            "failed_approach": "Long RFC style explanation",
            "successful_approach": "Simple access-control analogy",
            "used_to_help_employee": "Not yet",
            "source": "seed_demo",
        },
        {
            "concept": "Git Merge Conflict",
            "employee_level": "Fresher",
            "task": "Feature branch merge",
            "problem": "Unsure how to resolve same-line conflicts",
            "ai_explanation": "Conflict marker walkthrough",
            "mentor_explanation": "Compare both edits and keep intended combined output.",
            "successful_explanation": "Line-by-line compare workflow",
            "outcome": "Resolved and merged",
            "technologies": "Git",
            "useful_analogy": "Two editors on same paragraph",
            "failed_approach": "Blindly choosing incoming changes",
            "successful_approach": "Intent-based manual resolution",
            "used_to_help_employee": "Developer C",
            "source": "seed_demo",
        },
        {
            "concept": "Missing API validation",
            "employee_level": "Junior",
            "task": "POST customer endpoint",
            "problem": "Skipped schema validation",
            "ai_explanation": "Mentioned optional validation",
            "mentor_explanation": "Validation is the quality gate before DB save.",
            "successful_explanation": "Quality gate framing",
            "outcome": "Validation added",
            "technologies": "FastAPI, Pydantic",
            "useful_analogy": "Airport security check",
            "failed_approach": "Treating validation as optional",
            "successful_approach": "Mandatory gate concept",
            "used_to_help_employee": "API intern batch",
            "source": "seed_demo",
        },
        {
            "concept": "SQL query performance issue",
            "employee_level": "Junior",
            "task": "Employee search API",
            "problem": "Slow list endpoint",
            "ai_explanation": "Suggested adding indexes and pagination",
            "mentor_explanation": "Start with explain plan then index hottest filters.",
            "successful_explanation": "Measure-first tuning",
            "outcome": "Latency reduced",
            "technologies": "SQLite, SQL",
            "useful_analogy": "Book index for quick lookup",
            "failed_approach": "Guessing indexes",
            "successful_approach": "Explain-plan-led optimization",
            "used_to_help_employee": "Backend intern",
            "source": "seed_demo",
        },
    ]

    conn = get_db()
    existing = conn.execute("SELECT COUNT(*) AS count FROM experiences").fetchone()["count"]
    if existing > 0:
        conn.close()
        return

    for item in demo_experiences:
        conn.execute(
            """
            INSERT INTO experiences (
                concept, employee_level, task, problem, ai_explanation, mentor_explanation,
                successful_explanation, outcome, technologies, useful_analogy,
                failed_approach, successful_approach, used_to_help_employee,
                source, hindsight_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["concept"],
                item["employee_level"],
                item["task"],
                item["problem"],
                item["ai_explanation"],
                item["mentor_explanation"],
                item["successful_explanation"],
                item["outcome"],
                item["technologies"],
                item["useful_analogy"],
                item["failed_approach"],
                item["successful_approach"],
                item["used_to_help_employee"],
                item["source"],
                None,
                now_iso(),
            ),
        )

    conn.commit()
    conn.close()


def default_demo_state() -> dict[str, Any]:
    return {
        "task": {
            "title": DEFAULT_TASK_TITLE,
            "assigned_employee": "Manu",
            "deadline": "Today",
            "status": "active",
            "steps": [
                {"label": step, "status": "todo" if idx > 1 else "done"}
                for idx, step in enumerate(DEFAULT_STEPS)
            ],
        },
        "employees": {
            "employeeA": {
                "name": "Manu",
                "level": "Fresher",
                "task": "Employee Registration API",
                "question": DEFAULT_QUESTION,
                "ai_attempts": 0,
                "stuck": False,
                "mentor_requested": False,
                "mentor_alert": None,
                "understood": False,
                "chat": [],
            },
            "employeeB": {
                "name": "Riya",
                "level": "Junior",
                "task": "Employee Registration API",
                "question": DEFAULT_QUESTION,
                "ai_attempts": 0,
                "stuck": False,
                "mentor_requested": False,
                "mentor_alert": None,
                "understood": False,
                "chat": [],
            },
        },
        "recent_blockers": [],
        "mentor_interventions": 0,
        "completed_tasks": 0,
        "active_tasks": 1,
        "blocked_employees": 0,
        "last_reset": now_iso(),
    }


def load_state() -> dict[str, Any]:
    conn = get_db()
    row = conn.execute("SELECT value FROM demo_state WHERE key = 'runtime'").fetchone()
    conn.close()
    if not row:
        state = default_demo_state()
        save_state(state)
        return state
    return json.loads(row["value"])


def save_state(state: dict[str, Any]) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO demo_state(key, value) VALUES('runtime', ?)",
        (json.dumps(state),),
    )
    conn.commit()
    conn.close()


def fetch_experiences(limit: int = 20) -> list[dict[str, Any]]:
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, concept, employee_level, task, problem, ai_explanation, mentor_explanation,
               successful_explanation, outcome, technologies, useful_analogy,
               failed_approach, successful_approach, used_to_help_employee, source,
               hindsight_id, created_at
          FROM experiences
      ORDER BY id DESC
         LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def local_recall(concept_query: str, task: str, employee_level: str) -> list[dict[str, Any]]:
    conn = get_db()
    rows = conn.execute(
        """
        SELECT *
          FROM experiences
         WHERE lower(problem) LIKE lower(?)
            OR lower(concept) LIKE lower(?)
            OR lower(task) LIKE lower(?)
      ORDER BY id DESC
         LIMIT 3
        """,
        (f"%{concept_query}%", f"%{concept_query}%", f"%{task}%"),
    ).fetchall()
    conn.close()

    filtered = []
    for row in rows:
        item = dict(row)
        if employee_level.lower() in item["employee_level"].lower() or "fresher" in item[
            "employee_level"
        ].lower():
            filtered.append(item)
    return filtered or [dict(row) for row in rows]


class AskPayload(BaseModel):
    employee_id: str = Field(pattern="^(employeeA|employeeB)$")
    question: str


class EmployeePayload(BaseModel):
    employee_id: str = Field(pattern="^(employeeA|employeeB)$")


class MentorResolvePayload(BaseModel):
    employee_id: str = Field(pattern="^(employeeA|employeeB)$")
    mentor_explanation: str


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_experiences()
    load_state()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/demo/run")
def run_demo() -> dict[str, Any]:
    state = default_demo_state()
    state["employees"]["employeeA"]["chat"] = [
        {"sender": "manager", "message": f"Assigned: {DEFAULT_TASK_TITLE}"},
        {
            "sender": "ai",
            "message": "I split your task into 6 steps and will guide you through each one.",
        },
    ]
    save_state(state)
    return compose_response(state)


@app.get("/api/demo/state")
def get_state() -> dict[str, Any]:
    state = load_state()
    return compose_response(state)


def compose_response(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": state,
        "memory_cards": fetch_experiences(),
        "team_learning_insights": {
            "label": "Demo seeded insights",
            "recurring_knowledge_gap": "API → Database connection",
            "employees_affected": 8,
            "successful_resolution": 6,
            "recommended_action": "Create a short internal learning module.",
        },
        "hindsight": {
            "enabled": hindsight.enabled,
            "base_url_configured": bool(os.getenv("HINDSIGHT_BASE_URL")),
        },
    }


@app.post("/api/demo/ask-ai")
async def ask_ai(payload: AskPayload) -> dict[str, Any]:
    state = load_state()
    employee = state["employees"].get(payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee["chat"].append({"sender": "employee", "message": payload.question})
    employee["ai_attempts"] += 1

    concept = "API to Database Flow"
    recalled = await hindsight.recall_experience(
        concept=concept,
        employee_level=employee["level"],
        task=employee["task"],
        top_k=3,
    )
    source = "hindsight"
    if not recalled:
        recalled = local_recall("database", employee["task"], employee["level"])
        source = "local_fallback"

    used_memory = False
    if payload.employee_id == "employeeB" and recalled:
        top = recalled[0].get("experience", recalled[0])
        mentor_explanation = top.get("mentor_explanation") or top.get("successful_explanation")
        analogy = top.get("useful_analogy", "real-world analogy")
        answer = (
            "🧠 Learned from previous team experience\n"
            "I found a previous successful explanation for a fresher on a similar API task. "
            f"A {analogy} analogy helped them understand this. "
            f"{mentor_explanation}"
        )
        used_memory = True
    else:
        answer = DEFAULT_AI_EXPLANATION

    employee["chat"].append({"sender": "ai", "message": answer})
    save_state(state)

    return {
        "answer": answer,
        "used_memory": used_memory,
        "memory_source": source,
        "matches": len(recalled),
        "state": state,
    }


@app.post("/api/demo/im-stuck")
def im_stuck(payload: EmployeePayload) -> dict[str, Any]:
    state = load_state()
    employee = state["employees"].get(payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee["stuck"] = True
    employee["ai_attempts"] += 1
    employee["chat"].append(
        {
            "sender": "system",
            "message": "AI assistance attempted. Still need help? Request Mentor.",
        }
    )

    state["blocked_employees"] = max(1, state["blocked_employees"])
    blocker = {
        "employee": employee["name"],
        "task": employee["task"],
        "blocker": "API → Database connection",
        "ai_attempts": employee["ai_attempts"],
        "status": "blocked",
    }
    state["recent_blockers"] = [blocker] + state["recent_blockers"][0:4]

    save_state(state)
    return {"state": state, "message": "Blocker recorded"}


@app.post("/api/demo/request-mentor")
def request_mentor(payload: EmployeePayload) -> dict[str, Any]:
    state = load_state()
    employee = state["employees"].get(payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee["mentor_requested"] = True
    employee["mentor_alert"] = {
        "employee": employee["name"],
        "employee_level": employee["level"],
        "task": employee["task"],
        "blocker": "API → Database connection",
        "ai_attempts": employee["ai_attempts"],
    }
    state["mentor_interventions"] += 1

    save_state(state)
    return {"state": state, "mentor_alert": employee["mentor_alert"]}


@app.post("/api/demo/mentor-resolve")
async def mentor_resolve(payload: MentorResolvePayload) -> dict[str, Any]:
    state = load_state()
    employee = state["employees"].get(payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    experience = {
        "concept": "API to Database Flow",
        "employee_level": employee["level"],
        "task": employee["task"],
        "problem": employee["question"],
        "ai_explanation": DEFAULT_AI_EXPLANATION,
        "mentor_explanation": payload.mentor_explanation,
        "successful_explanation": payload.mentor_explanation,
        "outcome": "Successfully understood",
        "technologies": ["FastAPI", "SQLAlchemy", "SQLite"],
        "useful_analogy": "Receptionist",
    }

    hindsight_result: dict[str, Any]
    try:
        hindsight_result = await hindsight.retain_experience(experience)
    except Exception:  # noqa: BLE001
        hindsight_result = {
            "stored": False,
            "provider": "error",
            "error": "Hindsight retain request failed",
            "id": None,
        }

    conn = get_db()
    conn.execute(
        """
        INSERT INTO experiences (
            concept, employee_level, task, problem, ai_explanation, mentor_explanation,
            successful_explanation, outcome, technologies, useful_analogy,
            failed_approach, successful_approach, used_to_help_employee,
            source, hindsight_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            experience["concept"],
            experience["employee_level"],
            experience["task"],
            experience["problem"],
            experience["ai_explanation"],
            experience["mentor_explanation"],
            experience["successful_explanation"],
            experience["outcome"],
            ", ".join(experience["technologies"]),
            experience["useful_analogy"],
            "Technical explanation only",
            "Mentor analogy explanation",
            "Employee B",
            "hindsight" if hindsight_result.get("stored") else "local_retained",
            hindsight_result.get("id"),
            now_iso(),
        ),
    )
    conn.commit()
    conn.close()

    employee["chat"].append({"sender": "mentor", "message": payload.mentor_explanation})
    employee["mentor_requested"] = False
    employee["stuck"] = False
    employee["understood"] = True
    employee["mentor_alert"] = None
    state["blocked_employees"] = 0

    for step in state["task"]["steps"]:
        step["status"] = "done"
    state["completed_tasks"] = 1
    state["active_tasks"] = 0
    save_state(state)

    return {
        "message": "Mentor resolution stored to Hindsight flow",
        "hindsight": hindsight_result,
        "state": state,
        "memory_cards": fetch_experiences(),
    }


@app.post("/api/demo/understood")
def understood(payload: EmployeePayload) -> dict[str, Any]:
    state = load_state()
    employee = state["employees"].get(payload.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee["understood"] = True
    employee["chat"].append({"sender": "employee", "message": "UNDERSTOOD"})
    save_state(state)
    return {"state": state}
