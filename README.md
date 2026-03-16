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


## Authentication

This API uses JWT bearer authentication for protected routes.

### Auth Flow 

1. Register a user with `/api/v1/auth/register`
2. Log in with `/api/v1/auth/login`
3. Copy the returned access token
4. Authorize in Swagger UI
5. Access protected routes like `/api/v1/users/me`

### Protected Route Example

- `GET /api/v1/users/me`

## Features Implemented

- User registration
- User login
- JWT authentication
- Current user endpoint
- Task CRUD
- Task ownership
- Soft delete

## Task Fields

- title
- description
- status
- priority
- due_date

## Initial Endpoints

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Users
- `GET /api/v1/users/me`

### Tasks
- `POST /api/v1/tasks`
- `GET /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`
- `PATCH /api/v1/tasks/{task_id}`
- `DELETE /api/v1/tasks/{task_id}`

## Task Query Features

The task listing endpoint supports:
- pagination
- filtering by status
- filtering by priority
- filtering by due date range
- search by title or description
- sorting by `created_at`, `due_date`, or `priority`

### Example Queries

- `GET /api/v1/tasks?page=1&page_size=10`
- `GET /api/v1/tasks?status=done`
- `GET /api/v1/tasks?priority=high`
- `GET /api/v1/tasks?search=bug`
- `GET /api/v1/tasks?sort_by=due_date&sort_order=desc`
- `GET /api/v1/tasks?status=todo&priority=high&search=bug`

## Core Entities

- Users
- Teams
- Team Members
- Tasks
- Comments

## Team Membership

Teams support multi-user collaboration through a membership table with role-based access.

When a user creates a team, they are automatically added as an `admin`.

Team admins can:
- add members
- remove members
- manage team resources

Regular members can:
- view teams they belong to
- view team membership

## Authorization and RBAC

This project combines ownership-based access control with simple team-based RBAC.

### Task permissions
- personal tasks are only visible to their creator
- team tasks are visible to members of the team
- task creator can update or delete their own task
- team admin can update or delete any task in their team
- only valid team members can be assigned to a team task
- only team admins can assign or reassign team tasks

### Team permissions
- all team members can view team resources
- only team admins can manage membership

## Comments

The API supports task comments for collaborative discussion.

Users can comment on:
- their own personal tasks
- team tasks in teams they belong to

### Comment permissions
- comment owner can update or delete their own comment
- team admin can delete comments on team tasks
- deleted comments are soft deleted and excluded from normal reads

## Logging

The API includes simple request logging middleware that records:
- HTTP method
- request path
- response status code
- request duration