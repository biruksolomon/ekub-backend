# Ekub — Digital Rotating Savings & Credit Association Backend

> **Tagline:** Manage your ekub group's contributions, turn orders, and payouts — reliably without spreadsheets.

---

## 1. Executive Summary

**Ekub (Amharic: እቁብ)** is a traditional Ethiopian rotating savings and credit association (ROSCA). Members contribute a fixed amount on a regular schedule (weekly/monthly), and during each round, one member receives the full pooled sum. This process continues iteratively until every participating member has received a payout exactly once.

This backend provides a clean, robust, and tested **FastAPI** RESTful service powering both organizers and members. It encapsulates domain business logic including turn order generation, eligibility verification before closing rounds, contribution logging, and member status tracking.

---

## 2. Core Business Rules

| Domain Entity | Business Rule |
|---|---|
| **Group** | Formed by an organizer with a fixed contribution amount, round frequency (`weekly` or `monthly`), and start date. Starts in `pending` state and becomes `active` when started. |
| **Membership & Turn Order** | Members join pending groups. Upon starting, turn order is established (sequential or randomized draw) and locked. Each turn corresponds 1:1 with a round. |
| **Round Generation** | Starting a group automatically generates $N$ rounds for $N$ members with scheduled due dates. |
| **Contribution** | Members pay the exact fixed amount for each open round. Contributions are logged individually by the organizer. |
| **Payout Eligibility & Round Closure** | A round can **only** be closed once **all** members have contributed for that round. Closing a round marks the designated member as paid out. |
| **Group Completion** | Once all $N$ rounds are closed, the group transitions to `completed`. |

---

## 3. Clean Architecture Design

This project strictly adheres to **Clean Architecture** principles, enforcing unidirectionally layered dependencies:

```
[ HTTP API Layer ]  --->  [ Services (Business Rules) ]  --->  [ Repositories (Data Access) ]  --->  [ SQLAlchemy Models ]
         |                            |                                   |
         v                            v                                   v
[ Pydantic Schemas ]       [ Custom Exceptions ]                   [ PostgreSQL Database ]
```

### Layer Responsibilities

- **`app/models/`**: SQLAlchemy 2.0 ORM entities. Maps database tables and relationships. No business logic.
- **`app/schemas/`**: Pydantic v2 request/response DTO contracts separating API contracts from DB models.
- **`app/repositories/`**: Isolated data access layer. Encapsulates async ORM queries.
- **`app/services/`**: Core domain logic (turn allocation, round generation, eligibility rules, contribution processing).
- **`app/api/`**: Thin FastAPI routers translating HTTP requests, injecting dependencies, and invoking services.
- **`app/core/`**: Cross-cutting utilities (config, JWT security, password hashing, global exception handlers).

---

## 4. Project Structure

```
ekub_backend/
├── alembic/
│   ├── versions/                    # Migration files
│   └── env.py                       # Alembic environment setup
├── alembic.ini                      # Alembic configuration
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app initialization & OpenAPI setup
│   │
│   ├── core/                        # Cross-cutting concerns
│   │   ├── config.py                # Pydantic Settings
│   │   ├── security.py              # JWT & password hashing (bcrypt)
│   │   └── exceptions.py            # Custom domain exceptions & handlers
│   │
│   ├── database.py                  # Async SQLAlchemy engine & sessionmaker
│   │
│   ├── models/                      # SQLAlchemy ORM Models
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── membership.py
│   │   ├── round.py
│   │   └── contribution.py
│   │
│   ├── schemas/                     # Pydantic Schemas / DTOs
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── membership.py
│   │   ├── round.py
│   │   └── contribution.py
│   │
│   ├── repositories/                # Async Data Access Layer
│   │   ├── user_repository.py
│   │   ├── group_repository.py
│   │   ├── membership_repository.py
│   │   ├── round_repository.py
│   │   └── contribution_repository.py
│   │
│   ├── services/                    # Business Logic Layer
│   │   ├── auth_service.py
│   │   ├── group_service.py
│   │   ├── round_service.py
│   │   └── contribution_service.py
│   │
│   ├── api/                         # FastAPI HTTP Layer
│   │   ├── deps.py                  # Dependency Injections
│   │   └── v1/
│   │       ├── router.py            # Combined APIRouter
│   │       ├── auth.py              # Auth endpoints (/auth/*)
│   │       ├── groups.py            # Group endpoints (/groups/*)
│   │       ├── rounds.py            # Round endpoints (/rounds/*)
│   │       └── members.py           # Member view endpoints (/members/*)
│   │
│   └── tests/                       # Async Pytest Suite
│       ├── conftest.py              # SQLite in-memory async session & client fixture
│       ├── test_group_service.py
│       ├── test_round_service.py
│       └── test_contribution_service.py
│
├── .env.example                     # Environment template
├── requirements.txt                 # Dependencies
├── Dockerfile                       # Container definition
├── docker-compose.yml               # API + PostgreSQL setup
└── README.md
```

---

## 5. API Endpoints Reference

### Authentication
- `POST /api/v1/auth/register` — Register a new organizer/member.
- `POST /api/v1/auth/login` — Authenticate and receive a Bearer JWT token.

### Groups
- `POST /api/v1/groups` — Create a new group (Organizer only).
- `GET /api/v1/groups/{id}` — Get group detail and member count.
- `POST /api/v1/groups/{id}/members` — Add a member to a pending group.
- `POST /api/v1/groups/{id}/start` — Lock turn order and generate all rounds.

### Rounds & Contributions
- `GET /api/v1/groups/{group_id}/rounds` — List all rounds for a group.
- `GET /api/v1/rounds/{id}` — Get round details with contribution status.
- `POST /api/v1/rounds/{id}/contributions` — Log a member's payment for a round (Organizer only).
- `POST /api/v1/rounds/{id}/close` — Close a round and mark payout sent (requires 100% member contributions).

### Member Portal
- `GET /api/v1/members/me/groups` — Get groups current user belongs to.
- `GET /api/v1/members/me/groups/{group_id}/status` — Get member's contribution history and payout date.

---

## 6. Quick Start & Local Development

### Option A: Running with Docker Compose (Recommended)

```bash
# 1. Clone the repository and navigate into ekub-backend
cd ekub-backend

# 2. Build and start containers (FastAPI + Postgres)
docker-compose up --build
```
The API server will be available at `http://localhost:8000`.
Open Interactive Swagger Documentation at `http://localhost:8000/docs`.

### Option B: Running Locally with Python Virtualenv

```bash
# 1. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment settings
cp .env.example .env

# 4. Run database migrations (Ensure PostgreSQL is running locally)
alembic upgrade head

# 5. Start Uvicorn development server
uvicorn app.main:app --reload --port 8000
```

---

## 7. Running Tests

The test suite uses `pytest` with `asyncio` and an isolated in-memory SQLite database:

```bash
pytest
```
