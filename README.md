# 🚀 Team Task Manager API

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-orange)
![Status](https://img.shields.io/badge/Status-Active-success)

A **production-style backend system** for managing users, teams, tasks, assignments, and comments — designed to simulate real-world SaaS collaboration workflows.

Built with **FastAPI, PostgreSQL, and Streamlit**, this project demonstrates backend engineering fundamentals including authentication, RBAC, modular architecture, and scalable query design.

---

## 🧠 Overview

Most CRUD projects stop at basic data operations.

This project goes further by modeling:

* multi-user collaboration
* role-based access control (RBAC)
* team-scoped data visibility
* task assignment constraints
* advanced querying patterns

> **Goal:** Build a backend that behaves like a real production system — not just a demo API.

---

## 🧱 System Architecture

```text
Client (Streamlit / API Consumer)
        ↓
FastAPI API Layer (Routing, Validation)
        ↓
Service Layer (Business Logic)
        ↓
Permission Layer (RBAC Rules)
        ↓
CRUD Layer (Database Access)
        ↓
PostgreSQL Database
```

### Why this matters

* separation of concerns
* scalable backend design
* clean business logic boundaries
* easier testing and maintenance

---

## ✨ Core Features

### 🔐 Authentication & Security

* JWT-based authentication
* secure password hashing (bcrypt)
* OAuth2-compatible login flow
* protected routes via dependency injection

---

### 👥 Multi-Tenant Team System

* users can belong to multiple teams
* automatic admin assignment on team creation
* role-based permissions (admin/member)
* strict membership validation

---

### 📋 Task Management

* personal and team-scoped tasks
* task assignment to team members
* validation of assignment constraints
* soft deletion for data integrity

---

### 💬 Collaboration Layer

* comments on tasks
* ownership-based permissions
* admin moderation capabilities
* full CRUD operations

---

### 🔎 Advanced Querying

Supports:

* pagination (`page`, `page_size`)
* filtering (status, priority)
* search (title, description)
* sorting (created_at, due_date)

> Designed to mimic real production APIs.

---

## 🧩 Core Data Model

| Entity      | Description                        |
| ----------- | ---------------------------------- |
| Users       | authenticated system users         |
| Teams       | collaborative groups               |
| TeamMembers | user-team relationships with roles |
| Tasks       | actionable work items              |
| Comments    | communication layer on tasks       |

---

## ⚙️ Tech Stack

### Backend

* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic

### Auth & Security

* JWT
* OAuth2PasswordRequestForm
* bcrypt

### Testing

* Pytest

### Frontend Demo

* Streamlit

---

## 🗂️ Project Structure

```text
team-task-manager-api/
│
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           └── health.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── crud/
│   └── services/
│
├── tests/
├── scripts/
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚡ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/SimbaMunatsi/team-task-manager-api.git
cd team-task-manager-api
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

#### Activate

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/team_task_manager
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
STREAMLIT_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

---

### 5. Run Database Migrations

```bash
alembic upgrade head
```

---

### 6. Start FastAPI Backend

```bash
uvicorn app.main:app --reload
```

API Docs:

```
http://127.0.0.1:8000/docs
```

---

### 7. Start Streamlit Frontend

```bash
streamlit run streamlit_app.py
```

App UI:

```
http://127.0.0.1:8501
```

---

## 🔐 Authentication Details

Login uses **OAuth2 form-based authentication**.

Required format:

```text
username=<email>
password=<password>
```

Include JWT token in requests:

```text
Authorization: Bearer <token>
```

---

## 🧪 Testing

Run tests:

```bash
pytest
```

### Coverage Includes

* authentication flow
* RBAC enforcement
* task CRUD operations
* team membership rules
* assignment validation
* comment system logic

---

## 🌱 Seed Data

```bash
python scripts/seed_data.py
```

Creates:

* demo users
* teams
* tasks
* comments

---

## 🖥️ Streamlit Demo Features

* user registration & login
* team creation and management
* task creation and assignment
* comment system
* filtering and searching tasks

---

## 🔄 Example System Flow

```text
User registers
    ↓
User logs in
    ↓
Creates team
    ↓
Adds members
    ↓
Creates tasks
    ↓
Assigns tasks
    ↓
Members collaborate via comments
```

---

## 📈 Engineering Decisions

### Why RBAC?

* enables team collaboration
* supports admin control
* reflects real SaaS systems

### Why Service Layer?

* isolates business logic
* improves testability
* avoids bloated route handlers

### Why Soft Deletes?

* preserves historical data
* prevents accidental loss
* production-aligned design

---

## 🚧 Future Improvements

* audit logging
* notifications system
* WebSocket real-time updates
* background jobs (Celery)
* Redis caching
* rate limiting
* CI/CD pipeline

---

## 👤 Author

**Simbarashe Munatsi**

---

## ⭐ Final Note

This project demonstrates backend engineering beyond CRUD.

It reflects the shift from:

> “building APIs” → **designing production-ready backend systems**

---
