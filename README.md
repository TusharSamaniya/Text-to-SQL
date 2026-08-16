# 🗄️ Text-to-SQL with a Clarification Engine

Ask questions about your company database in plain English, and get the
answer as a table — with a built-in **clarification engine** that detects
vague questions and asks you what you mean before generating SQL.

> *"Show me last month's best customers"* → *"What does 'best' mean?*
> *1) highest total revenue  2) most orders  3) highest average order"*
> → pick one → real answer from your database.

Built as a complete learning project: **Python + Flask + Google Gemini +
PostgreSQL on the backend, React on the frontend.**

---

## ✨ Features

- **Natural language → SQL**: Gemini generates PostgreSQL from your words,
  guided by your live database schema and example question→SQL pairs.
- **Clarification engine**: a fast rule-list (`best`, `top`, `recent`, …)
  **plus** a Gemini deep-judge catch vague language and ask the user
  multiple-choice follow-ups before answering.
- **Safe execution**: read-only queries only, a row cap on results, and
  multi-statement SQL is rejected — your data can't be modified.
- **Self-correction loop**: if the generated SQL errors, the error is sent
  back to Gemini to fix itself (up to 2 repairs) before giving up honestly.
- **Explainability**: every answer shows the exact SQL that was run.
- **Audit log**: every question → SQL → result is saved to `history.jsonl`.
- **Session state**: each conversation is remembered (pending clarifications
  live per session).

---

## 🏗️ Architecture

```
English question
      │
      ▼
┌───────────────────────────┐
│  Clarification engine     │  rules (fast) + Gemini (deep judge)
│  ambiguous? → ask user    │  user's pick becomes the next question
└───────────────────────────┘
      │ clear question
      ▼
┌───────────────────────────┐
│  SQL generation           │  Gemini + schema + few-shot examples
└───────────────────────────┘
      │ SQL
      ▼
┌───────────────────────────┐
│  Safe execution           │  read-only, row cap, self-correction loop
└───────────────────────────┘
      │ rows
      ▼
     JSON → React UI (table + the generated SQL)
```

**Three layers, kept separate** (this is what makes it testable and
deployable):

| Layer | Tech | Where it lives |
|---|---|---|
| Frontend | React (Vite) | `frontend/` |
| API | Flask | `backend/app.py` |
| AI + Data | Gemini + PostgreSQL | `backend/` modules |

The AI logic lives in pure Python modules (`pipeline.py`, `llm.py`,
`clarifier.py`, `db.py`) — Flask is just a thin wrapper.

---

## 🧰 Tech stack

- **Python 3** + Flask + Flask-CORS + psycopg2 + google-genai + python-dotenv
- **Google Gemini** (free tier — model name lives in `.env`, currently
  `gemini-flash-lite-latest`)
- **PostgreSQL** (local via pgAdmin; cloud-ready — see *Different database*)
- **React + Vite** (JavaScript)

---

## 🚀 Setup (from scratch)

### 1. Backend

```bash
cd backend
python -m venv venv                 # create the virtual environment
venv\Scripts\activate               # Windows; source venv/Scripts/activate in Git Bash
pip install -r requirements.txt     # install dependencies
```

### 2. Configuration

Copy the template and fill in your values:

```bash
copy .env.example .env              # Windows cmd
# or: cp .env.example .env          # Git Bash
```

`backend/.env` needs:
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
GEMINI_API_KEY=your_gemini_key_here     # free from aistudio.google.com
MODEL_NAME=gemini-flash-lite-latest
```
`.env` is never committed (see `.gitignore`).

### 3. Database (sample data)

In pgAdmin: create a database (e.g. `company_db`), open the Query Tool, and
run `data/schema.sql` first, then `data/seed.sql`. The seed generates
~50 customers / 400 orders / 400 payments deterministically.

Verify: `SELECT COUNT(*) FROM customers;` → `50`

### 4. Run it (two terminals)

```bash
# Terminal 1 — API (http://127.0.0.1:5000)
cd backend && python app.py

# Terminal 2 — frontend (http://localhost:5173)
cd frontend && npm install && npm run dev
```

Open **http://localhost:5173** and ask something like:
- `How many new customers signed up last month?`
- `Show me last month's best customers` ← watch the clarification dialog!

---

## 🔌 API

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/api/health` | GET | — | `{"status": "ok"}` |
| `/api/ask` | POST | `{"session_id": "...", "question": "..."}` | answer rows **or** `needs_clarification` |
| `/api/ask` | POST | `{"session_id": "...", "choice": 0}` | answer for the picked option |

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc", "question": "How many customers live in Mumbai?"}'
```

```json
{
  "session_id": "abc",
  "needs_clarification": false,
  "question": "How many customers live in Mumbai?",
  "columns": ["count"],
  "rows": [["7"]],
  "sql": "SELECT COUNT(*) FROM customers WHERE city = 'Mumbai';"
}
```

The frontend sends the same `session_id` on every request so the server can
remember pending clarifications.

---

## 🗄️ Point it at a different database

The system connects to **any PostgreSQL database** — the schema is read
automatically (introspection), nothing is hard-coded. One copy of the
project = one `DATABASE_URL`:

- **Local PostgreSQL** — as above.
- **Cloud PostgreSQL** (Neon / Supabase / RDS) — just put the cloud URL in
  `.env`. Same code, no changes. That's the Phase 5 deployment path.
- **A different schema** — it connects fine, but the example question→SQL
  pairs in `few_shots.py` are tuned to this project's schema, so accuracy
  drops on unfamiliar tables. (Future improvement: generate examples
  dynamically from the live schema.)

**Model for sharing:** every company/user runs their **own copy** with their
**own** `DATABASE_URL` (self-host). Users never touch your database and your
server never stores strangers' credentials. A multi-tenant SaaS where
untrusted users submit arbitrary database URLs is a security-sensitive
design and intentionally out of scope.

---

## ✅ Tests

There are small test files for every subsystem (run from `backend/`):

| Command | What it proves |
|---|---|
| `python test_db.py` | Python ↔ PostgreSQL works, rows print |
| `python test_safe_exec.py` | read-only guard + row cap hold |
| `python test_loop.py` | self-correction loop (incl. forced failure) |
| `python test_detect.py` / `test_ambiguity_ai.py` / `test_combine.py` | ambiguity detection layers |
| `python test_clarify.py` / `test_clarify_flow.py` | clarification options + full dialog over HTTP |
| `python test_safety.py` | adversarial inputs — database unharmed |
| `python test_logger.py` | audit log writes parseable JSONL |
| `python run_evaluation.py` | 20-question scored benchmark (~5 min, needs API quota) |

The 20-question test set lives in `evaluation.py`; the current baseline and
failure analysis are in `docs/evaluation_report.md`.

---

## 📁 Project structure

```
Text to SQL/
├── backend/
│   ├── app.py            Flask API (state machine: ask / clarify / answer)
│   ├── pipeline.py       main flow: question → SQL → results (self-correcting)
│   ├── clarifier.py      ambiguity rules + Gemini judge + options
│   ├── prompts.py        my capabilities templates
│   ├── few_shots.py      example question→SQL pairs
│   ├── llm.py            the only file that talks to Gemini
│   ├── db.py             the only file that talks to PostgreSQL
│   ├── sessions.py       pending clarifications per session
│   ├── logger.py         JSONL audit log
│   ├── config.py         reads .env
│   ├── evaluation.py     the 20-question test set
│   ├── run_evaluation.py scored benchmark
│   ├── history.jsonl     audit trail (grows)
│   └── .env / .env.example
├── frontend/             React + Vite chat UI
├── data/
│   ├── schema.sql        table blueprint (3 tables)
│   └── seed.sql          generates the sample data
├── docs/
│   └── evaluation_report.md
└── plan.txt              the original build plan
```

---

## 🛣️ Roadmap (already planned)

1. **Hardening & evaluation** — ✅ done: 20-question benchmark, audit log,
   adversarial safety review.
2. **Deployment for team use** — move the database to a cloud PostgreSQL,
   deploy the API (Render / Railway / PythonAnywhere), deploy the frontend
   (Vercel / Netlify), use a read-only DB user for the app.
3. **Ideas beyond:** dynamic few-shots from the live schema, clarification
   round limit, logging rotation, per-tenant deployments.

---

## 📜 License

Personal learning project. Free to use, adapt, and learn from.
