# 📄 Document Intelligence Platform (FastAPI + LLM)

A minimal, production-style document intelligence pipeline that processes structured extraction outputs through validation, AI-assisted matching, and decision routing.

---

## 🚀 Overview

This project simulates a downstream system that processes extracted document data using a composable workflow:

```
Ingest → Validate → Match → Decide → Deliver
```

The system is configuration-driven and enriches a JSON **Execution Envelope** without modifying upstream data.

---

## 🛠️ Tech Stack

* Python 3.11+
* FastAPI
* Pydantic v2
* SQLAlchemy (Async)
* PostgreSQL
* Alembic (migrations)
* httpx (LLM calls)
* pytest

---

## 📁 Project Structure

```
doc-intelligence-platform/
│
├── app/
│   ├── main.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── services/
│
├── alembic/
├── tests/
├── .env
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup (Run in 3 Commands)

### 1️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

### 2️⃣ Configure environment

Create `.env` file:

```
DATABASE_URL=postgresql+asyncpg://postgres:1234@localhost:5432/docintel
OPENAI_API_KEY=your_key_here
```

---

### 3️⃣ Run server

```
uvicorn app.main:app --reload
```

---

## 📊 API Docs

* Swagger UI → http://127.0.0.1:8000/docs
* ReDoc → http://127.0.0.1:8000/redoc

---

## 🧩 Endpoints

| Endpoint    | Description                  |
| ----------- | ---------------------------- |
| `/health`   | Service health check         |
| `/validate` | Validate envelope            |
| `/match`    | LLM-based commodity matching |
| `/process`  | Full pipeline execution      |

---

## 🧠 Core Features

### ✅ Validation Service

* Required field checks
* Confidence threshold validation
* Date validation (not future / not >365 days old)
* Decision routing:

  * `auto_approve`
  * `hitl_review`
  * `rejected`
* Audit logging

---

### 🤖 LLM Matching

* Triggered when commodity_code confidence is low
* Uses fallback `commodity_desc`
* Returns:

  * matched_code
  * confidence
  * rationale
* Graceful failure handling (never crashes pipeline)

---

### 🔄 Pipeline

* `/process` executes:

  * Validation → Matching → Decision
* Fully enriched envelope returned

---

## 🗄️ Database (PostgreSQL)

### Run migrations

```
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### Important Note

* App uses async DB (`asyncpg`)
* Alembic uses sync DB (`psycopg2`)

---

## 🧪 Running Tests

```
pytest
```

---

## ⚠️ Known Trade-offs

* LLM call uses mock fallback (replaceable with OpenAI)
* Minimal schema (audit_logs only)
* No authentication layer
* No background jobs (Celery skipped)

---

## 🧠 Design Decisions

* Envelope is immutable → only enriched
* Configuration-driven (threshold from input)
* LLM isolated → easy to swap providers
* Failure-safe → no pipeline crashes
* Audit-first → every action traceable

---

## 🔮 What I Would Improve

* Add Redis + Celery for async processing
* Introduce caching for LLM responses
* Add multi-tenant DB schema
* Improve observability (structured logging)
* Add retry + circuit breaker for LLM calls

---

## 🎯 Demo Flow

1. Open Swagger → `/docs`
2. Use `/process`
3. Paste sample JSON envelope
4. Execute → view enriched response


## 📌 Status

✅ Validation complete
✅ LLM matching integrated
✅ Pipeline working
✅ PostgreSQL connected
✅ Migrations configured

---

## 🙌 Author

Built as part of Senior AI Developer evaluation task.
