# Team Task Manager API

A production-aware FastAPI backend for managing users, teams, tasks, assignments, and comments with JWT authentication, RBAC, filtering, pagination, and Docker support.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT Authentication
- Pytest
- Docker

## Project Structure

```text
app/
api/
core/
db/
models/
schemas/
crud/
services/
tests/



---

# Full Day 1 file tree

```text
team-task-manager-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── crud/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
│
├── tests/
├── .env
├── .env.example
├── README.md
└── requirements.txt
'''


## Setup

1. Create and activate a virtual environment
2. Install dependencies with `pip install -r requirements.txt`
3. Configure your `.env` file
4. Create the PostgreSQL database
5. Run `alembic upgrade head`
6. Start the API with `uvicorn app.main:app --reload`