# Scribes — Backend Guide (Comprehensive)

**Version:** 1.0
**Last Updated:** 2025-08-24
**Owner:** Joshua

> Purpose: single-source, developer-focused guide for implementing the Scribes backend. This document walks from authentication all the way to APIs, workers, testing, deployment, and maintenance. Treat it as your backend handbook.

---

## Table of Contents
1. Overview & Architecture
2. Prerequisites & Local Dev Setup
3. Repo Layout (concrete)
4. Environment Variables (.env.example)
5. Database & Migrations (Alembic)
6. Authentication (JWT + Refresh + Passkeys)
7. Models (SQLAlchemy) — canonical definitions
8. Repositories (data access pattern)
9. Services (business logic)
10. Routers / Endpoints (FastAPI)
11. DTOs & Schemas (Pydantic)
12. Workers (Celery/RQ) — tasks and scheduling
13. Adapters: AI, Scripture, Storage, Notifier
14. Error Handling & API Contract
15. Logging, Tracing & Observability
16. Testing Strategy (unit, integration, e2e)
17. CI/CD & Deployment (Docker, Docker Compose, Kubernetes notes)
18. Security Checklist & Best Practices
19. Useful commands & scripts
20. Implementation Roadmap & Milestones

---

## 1 — Overview & Architecture (short)
Scribes backend is a REST API built with **FastAPI**. Core responsibilities:
- Auth & user profiles
- Notes CRUD + tagging (scripture, topics)
- CrossRef graph building (worker)
- Reminders scheduling (worker)
- Exports (worker) and file blobs in object store
- Assistant/AI interactions via adapters

Key runtime components:
- FastAPI app (HTTP)
- Postgres (persistent relational data)
- Redis (cache + broker)
- Worker pool (Celery or RQ)
- Object storage (S3-compatible)
- Optional: PgVector for semantic search

Diagram (logical):
```
[Client Flutter] → [API (FastAPI)] → [Postgres]
                        ↓               ↑
                     [Redis] ←→ [Workers]
                        ↓
                   [Object Storage]
                        ↓
                   [External AI / Bible APIs]
```

---

## 2 — Prerequisites & Local Dev Setup
### System tools
- Python 3.11+ (3.10 is acceptable if 3.11 unavailable)
- PostgreSQL 14+ (local or Docker)
- Redis (local or Docker)
- Docker & Docker Compose (recommended for reproducibility)
- Node/npm (only if you run frontend locally)

### Python dependencies (example)
- fastapi
- uvicorn[standard]
- sqlalchemy[psycopg]
- alembic
- pydantic
- python-dotenv
- passlib[bcrypt]
- pyjwt or jose
- celery[redis] or rq
- boto3 (if using S3)
- httpx or requests

### Recommended dev setup via Docker Compose (minimal)
Provide and maintain a `docker-compose.dev.yml` with services: `postgres`, `redis`, `minio` (or localstack S3), and `backend` (built image). This keeps everyone on the same environment.

---

## 3 — Repo Layout (concrete)
A strict layout avoids confusion. Use this exact structure in the backend root:
```
backend/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ deps.py
│  ├─ logging_config.py
│  ├─ security/
│  │  ├─ auth.py
│  │  └─ crypto.py
│  ├─ db/
│  │  ├─ session.py
│  │  ├─ models.py
│  │  ├─ repositories/
│  │  └─ migrations/
│  ├─ schemas/
│  ├─ services/
│  ├─ routers/
│  ├─ workers/
│  ├─ adapters/
│  ├─ utils/
│  └─ docs/
├─ tests/
├─ alembic.ini
├─ Dockerfile
├─ docker-compose.dev.yml
├─ pyproject.toml (or requirements.txt)
├─ .env.example
└─ README.md
```

Notes:
- Keep business logic in `services/` — routers should be thin.
- Repositories encapsulate DB queries.
- Adapters are external system connectors (AI, Bible API, S3, notifier).

---

## 4 — Environment Variables (.env.example)
Provide a template and require any contributor to copy to `.env`.
```
# Server
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=changeme_really_use_long_random
# Database
DATABASE_URL=postgresql+psycopg://scribes_user:password@localhost:5432/scribes_db
# Redis
REDIS_URL=redis://localhost:6379/0
# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
# JWT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
# AWS / S3
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET=scribes-uploads
# AI provider (example)
AI_PROVIDER_URL=https://api.openai.com/v1
AI_API_KEY=sk-xxx
# Misc
LOG_LEVEL=INFO
```

---

## 5 — Database & Migrations (Alembic)
### Setup
1. Add `sqlalchemy` and `alembic` to dependencies.
2. Create `app/db/session.py` to initialize SQLAlchemy engine from `DATABASE_URL`.
3. `alembic init migrations` → edit `env.py` to load `DATABASE_URL` from env and import `target_metadata` from `models.py` if using SQLAlchemy models.

### Migrations workflow
- `alembic revision -m "create initial schema" --autogenerate` (if you use models)
- `alembic upgrade head` to apply migrations
- Commit generated migration files to git

### Seed data
Create dedicated seed migration or script `scripts/seed_dev.py` that inserts a dev user and example note(s).

---

## 6 — Authentication (JWT + Refresh + Passkeys)
### Concepts (simple)
- **Access Token (JWT)**: short-lived token included in `Authorization: Bearer <token>`.
- **Refresh Token**: long-lived, stored securely (httpOnly cookie, or DB) used to get new access tokens.
- **Passkeys**: optional; WebAuthn flow for passwordless login (R2/opt-in).

### Endpoints
- `POST /v1/auth/signup` — create new user (email, password).
- `POST /v1/auth/login` — verify password, return `access_token` & `refresh_token`.
- `POST /v1/auth/refresh` — accept refresh token (cookie or body) and issue new access token.
- `POST /v1/auth/logout` — revoke refresh token.
- `GET /v1/auth/me` — return current user profile.

### Implementation snippets (FastAPI patterns)
- Use `passlib` `bcrypt` for hashing passwords.
- Use `pyjwt` or `python-jose` for generating tokens. Store `SECRET_KEY` in env.
- Example token creation (pseudocode):
```python
from datetime import datetime, timedelta
import jwt

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token
```

- `get_current_user` dependency:
  - Read `Authorization` header, verify JWT signature/exp.
  - Load user from DB using `sub` claim (user id/email).
  - Raise `HTTPException(status_code=401)` on failure.

### Refresh token storage patterns
- **Stateless**: sign refresh tokens as JWT and rotate them — requires rotation strategy to mitigate replay.
- **Stateful**: store refresh token records in DB (user_id, jti, expiry). On logout delete record.

Recommendation: start with stateful refresh tokens stored in DB (clearer revocation) and consider rotation in R2.

---

## 7 — Models (SQLAlchemy) — canonical definitions
Keep models in `app/db/models.py`. Use `UUID` primary keys and `created_at/updated_at` timestamps.

Example (simplified):
```python
from sqlalchemy import Column, String, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

class User(Base):
    __tablename__ = 'app_user'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    display_name = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Note(Base):
    __tablename__ = 'note'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('app_user.id', ondelete='CASCADE'))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    date_time = Column(TIMESTAMP(timezone=True), nullable=False)
    tags = Column(ARRAY(String))
    topics = Column(ARRAY(String))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now(), server_default=func.now())
```

Include models for `ScriptureTag`, `CrossRef`, `Reminder`, `PrayerPoint`, `Circle`, `CircleMember`, and `SharedItem` following the SRS schema.

Indexing and FTS: add `tsvector` materialized column for search and a GIN index for arrays.

---

## 8 — Repositories (data access pattern)
Create thin repository classes under `app/db/repositories/` that accept a `db: Session` and perform raw queries. Keep them small and testable.

Example `notes_repo.py` functions:
- `create_note(db, user_id, data)`
- `get_note_by_id(db, note_id)`
- `list_notes(db, user_id, filters, limit, offset)`
- `update_note(db, note_id, changes)`
- `delete_note(db, note_id)`

Why repos?
- Centralizes SQL/ORM logic
- Easier to mock in service/unit tests

---

## 9 — Services (business logic)
Services call repositories and adapters.
Examples in `app/services/notes_service.py`:
- `create_note_with_tags(user, note_data)` → create note, detect scripture tags (adapter), enqueue crossref job
- `update_note_and_reindex(note_id, data)` → update content, update embeddings, re-run crossref

Services are where we: ensure permission checks, trigger worker jobs, apply domain rules.

---

## 10 — Routers / Endpoints (FastAPI)
Create routers in `app/routers/` and include under `/v1` with tags and dependencies.

Minimal router example for Notes (`app/routers/notes_router.py`):
```python
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.note_schemas import NoteCreate, NoteRead
from app.deps import get_db, get_current_user

router = APIRouter(prefix='/v1/notes', tags=['notes'])

@router.post('/', response_model=NoteRead)
def create_note(payload: NoteCreate, db=Depends(get_db), user=Depends(get_current_user)):
    note = notes_service.create_note_with_tags(db, user.id, payload)
    return note
```

Document all endpoints in OpenAPI and provide example bodies in `app/docs/examples/`.

---

## 11 — DTOs & Schemas (Pydantic)
Keep API schemas in `app/schemas/`.
- `NoteCreate` / `NoteUpdate` / `NoteRead`
- `UserCreate`, `UserRead`
- `ReminderCreate`, `ReminderRead`
- `Token`, `TokenPayload`

Pydantic models should be small and focused. Avoid exposing internal fields (like `hashed_password`).

---

## 12 — Workers (Celery/RQ) — tasks and scheduling
### Celery recommended pattern
- Broker: Redis
- Backend: Redis or DB (for result storage, optional)

Define tasks in `app/workers/tasks_*`:
- `build_crossrefs(note_id)`
- `generate_export(job_id, user_id, scope)`
- `send_reminder(reminder_id)`

Task flow example (build_crossrefs):
1. Task loads note & scripture tags
2. Compute embeddings via adapter
3. Run similarity queries or exact scripture matching
4. Insert `cross_ref` rows
5. Emit cache invalidation for note graph

Schedule reminders using Celery beat or a scheduled job that enqueues `send_reminder` when `scheduled_at <= now()`.

---

## 13 — Adapters: AI, Scripture, Storage, Notifier
Adapters are the only modules that directly call external systems.
- `ai_provider.py`: wraps LLM calls; implements retries and safety checks.
- `scripture_lookup.py`: resolves canonical references & fetches verse text (cache results).
- `storage.py`: S3-compatible upload/download helpers (boto3 wrapper).
- `notifier.py`: push/email wrapper (FCM, APNs, SMTP).

Always wrap external calls with timeouts and circuit-breaker patterns (retry polite backoff).

---

## 14 — Error Handling & API Contract
Standardize errors with a JSON envelope:
```json
{ "error": { "code": "NOTE_NOT_FOUND", "message": "Note not found", "traceId": "..." } }
```
- Use `HTTPException(status_code, detail=...)` for common cases
- Register a global exception handler in `main.py` for generic exceptions and to inject traceId
- Map database constraint errors to user-friendly errors (e.g., unique email conflict)

---

## 15 — Logging, Tracing & Observability
- Use structured logging (JSON) with `structlog` or `logging` + formatter
- Include `trace_id` in logs; generate in request middleware
- Optionally instrument with OpenTelemetry for traces (FastAPI middleware exists)
- Export errors to Sentry (Sentry SDK)
- Metrics: Prometheus exporter for request latency, paraphrase latency, worker failures

---

## 16 — Testing Strategy
- Unit tests: services & repos (mock DB session / use sqlite in-memory for quick tests)
- Integration tests: test HTTP routes with TestClient and a test DB (docker-compose test stack)
- E2E: run full stack (backend + db + redis) using pytest-docker or GitHub Actions environment

Example test (pytest):
```python
def test_create_note_authorized(client, auth_headers):
    payload = {"title": "hello", "content": "body", "date_time": "2025-01-01T10:00:00Z"}
    r = client.post('/v1/notes', json=payload, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()['title'] == 'hello'
```

---

## 17 — CI/CD & Deployment
- GitHub Actions: run lint, unit tests, build docker image, run migrations on deploy
- Dockerfile: multi-stage build (install deps → copy source → run uvicorn)
- docker-compose.dev.yml for local dev with Postgres/Redis/Minio
- Production: prefer managed Postgres + Redis, run backend in k8s or Fargate
- Use feature flags for risky features (Assistant, Community Mode)

---

## 18 — Security Checklist & Best Practices
- Use TLS at ingress (Cloud provider or reverse proxy)
- Sign JWTs with a strong secret; rotate keys periodically (key id/kid header)
- Store refresh tokens server-side for revocation
- Rate limit auth endpoints (per IP & per account)
- Encrypt sensitive fields at rest (note.content field-level encryption optional)
- Sanitize and validate all input from adapters (never trust external APIs)
- CORS: allow only app domains in production

---

## 19 — Useful commands & scripts
- Run dev server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Alembic: `alembic revision --autogenerate -m "msg"`; `alembic upgrade head`
- Create seed data: `python scripts/seed_dev.py`
- Run celery worker: `celery -A app.workers.worker worker --loglevel=info`
- Run celery beat (scheduler): `celery -A app.workers.worker beat --loglevel=info`
- Run tests: `pytest -q`

---

## 20 — Implementation Roadmap & Milestones (suggested)
**Sprint 0 — Foundation (1 week)**
- Repo skeleton, env config, logging, healthcheck endpoint
- JWT auth & `/v1/auth/me` + tests

**Sprint 1 — Notes CRUD (2 weeks)**
- Models, repos, services, routers for notes
- Pydantic schemas & validation
- Alembic initial migration + seed
- Simple client integration test

**Sprint 2 — Scripture Tagging + CrossRef (2 weeks)**
- Adapters for scripture lookup
- Worker + `build_crossrefs` task
- CrossRef storage & simple UI hooks

**Sprint 3 — Reminders + Scheduler (2 weeks)**
- Reminder model, API, worker for `send_reminder`
- Spaced repetition algorithm

**Sprint 4 — Exports & Assistant (2–3 weeks)**
- Export job (PDF/MD), S3 upload
- AI paraphrase endpoint, safety checks
- Assistant service basics

**Sprint 5 — Circles & Sharing (2 weeks)**
- Circles model, invite flow, share endpoints
- Access control and permission checks

**Sprint 6 — Hardening & Release (2 weeks)**
- Load tests, security review, logging/tracing finalization
- Release to beta (TestFlight / Play Store)

---

### Final notes (mentor tips)
- Keep routers thin, services pure logic, adapters as external boundaries.
- Write tests before adding complex logic (crossref, paraphrase).
- Version your API (`/v1`) and use feature flags to gate experiments.
- If uncertain about pgvector or heavy AI features, defer them behind flags and focus on robust simple features first.

---

If you want, Joshua, I can now:
- generate a ready-to-commit `backend/` scaffold (files with starter code), or
- produce the Alembic `initial` migration file for the schema, or
- produce ready-made FastAPI route & service code for Notes CRUD (complete with tests).

Tell me which and I’ll produce it next.

