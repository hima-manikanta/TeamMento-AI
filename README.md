# TeamMento AI

**Every problem solved by your team becomes knowledge for the next employee.**

TeamMento AI is a hackathon MVP that demonstrates one complete memory-driven mentoring workflow for software teams.

## Problem
Freshers and juniors often get stuck on the same technical concepts, while mentors repeatedly explain the same thing and that knowledge is lost.

## Solution
TeamMento AI guides employees with AI, escalates unresolved blockers to mentors, stores successful mentor explanations as experience, and reuses those experiences for the next employee.

## Why Hindsight Memory Matters
Without memory: **Question → Generic AI answer**

With TeamMento:
**Question → Recall previous team experience → Find successful approach → Adapt guidance → Better outcome → Store new memory**

## Core Features Implemented
- 3-screen MVP UI (Manager Dashboard, Employee/AI Mentor, Team Memory)
- Single end-to-end scenario: **Employee Registration REST API (FastAPI)**
- AI task breakdown into 6 guided steps
- Blocker flow: Ask AI → Still stuck → Request mentor
- Mentor intervention alert with attempts count
- Hindsight integration service:
  - `retain_experience()` after mentor resolution
  - `recall_experience()` before helping Employee B
- Team memory cards with failed vs successful approaches
- Team learning insights panel (seeded demo data)
- One-click **Run Demo** reset flow

## Architecture
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS
- **Backend:** FastAPI (Python)
- **Database:** SQLite (`backend/teammento.db`)
- **Memory:** Hindsight via `backend/services/hindsight_service.py`
- **Runtime flow:** Frontend calls backend demo APIs; backend persists and recalls memory

## Memory Learning Loop (Implemented)
1. Employee A asks: “I don't understand how the API connects to the database.”
2. AI explains.
3. Employee A is still stuck and requests mentor.
4. Mentor provides receptionist analogy.
5. Backend calls `retain_experience()` and stores result + local mirror.
6. Employee B asks similar question.
7. Backend calls `recall_experience()`.
8. AI response uses recalled successful explanation and shows:
   - `🧠 Learned from previous team experience`
9. Team Memory screen shows the learned experience.

## Demo Scenario
Primary scenario in this MVP:
- Manager assigns **Build an Employee Registration REST API using FastAPI** to Manu.
- AI mentor gives step-by-step plan.
- Manu gets stuck on API → database connection.
- Mentor resolves blocker.
- Memory retained.
- Riya (second employee) asks same blocker.
- TeamMento recalls prior successful explanation and improves guidance.

## Team Memory Seed Data
The memory screen is pre-seeded with realistic experiences:
1. API/database explanation
2. JWT authentication problem
3. Git merge conflict
4. Missing API validation
5. SQL query performance issue

At least two include explicit failed approach → successful approach outcomes.

## Project Structure
```text
TeamMento-AI/
├── backend/
│   ├── main.py
│   └── services/
│       └── hindsight_service.py
├── frontend/
│   └── src/app/page.tsx
├── docs/
├── screenshots/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup Instructions
### 1) Clone and enter
```bash
git clone <repo-url>
cd TeamMento-AI
```

### 2) Create environment file
```bash
cp .env.example .env
```

### 3) Backend setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4) Frontend setup
```bash
cd frontend
npm install
cd ..
```

## Environment Variables
In `.env`:
```env
LLM_API_KEY=
HINDSIGHT_API_KEY=
HINDSIGHT_BASE_URL=
DATABASE_URL=sqlite:///./backend/teammento.db
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run Commands
### Start backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Start frontend (new terminal)
```bash
cd frontend
npm run dev
```

Open: `http://localhost:3000`

## Hindsight Integration Details
Service file: `backend/services/hindsight_service.py`
- `retain_experience(experience)` sends POST to:
  - `POST {HINDSIGHT_BASE_URL}/v1/experiences/retain`
- `recall_experience(concept, employee_level, task)` sends POST to:
  - `POST {HINDSIGHT_BASE_URL}/v1/experiences/recall`

When Hindsight is unavailable, the app keeps a local retained mirror for demo continuity, but still attempts Hindsight calls whenever configured.

## Screenshots
Add submission screenshots in `/screenshots` for:
1. Manager Dashboard
2. Employee/Mentor flow
3. Team Memory with learned experience card

## Limitations (Current Round MVP)
- Uses a single focused scenario for 2–3 minute demo.
- Mentor actions are manually triggered in UI.
- Team insight metrics are seeded demo values.
- LLM response generation is template-driven for deterministic judging flow.
- Hindsight endpoint path assumptions may require small URL adaptation to your account setup.

## Future Scope
- Multi-task and multi-mentor workflows
- Stronger personalization via richer employee profiles
- Automatic mentor routing
- Integrations (Teams/Jira/GitHub/Azure DevOps)
- Deeper analytics and learning modules

---

## 2-Minute Judge Demo Script
1. Click **Run Demo**.
2. Open **Manager Dashboard** and show assigned FastAPI task + stats.
3. Go to **Employee / AI Mentor** (Employee A Manu).
4. Click **Ask AI** with API→DB question.
5. Click **I'm Stuck** then **Request Mentor**.
6. Show Mentor Alert details (employee, blocker, AI attempts).
7. Click **Save to Hindsight** with receptionist explanation.
8. Switch employee selector to **Employee B (Riya)**.
9. Ask the same question.
10. Show banner: **🧠 Learned from previous team experience**.
11. Open **Team Memory** and show learned card + insights.
12. Conclude: TeamMento improved guidance using previous team experience.
