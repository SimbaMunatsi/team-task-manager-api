import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Allow imports from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.db.base import Base
from app.db.session import get_db
from app.main import app


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def user_payload():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "strongpass123",
    }


@pytest.fixture
def second_user_payload():
    return {
        "username": "seconduser",
        "email": "seconduser@example.com",
        "password": "strongpass123",
    }


@pytest.fixture
def create_user(client, user_payload):
    response = client.post("/api/v1/auth/register", json=user_payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def create_second_user(client, second_user_payload):
    response = client.post("/api/v1/auth/register", json=second_user_payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(client, user_payload, create_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_payload["email"],
            "password": user_payload["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(client, second_user_payload, create_second_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": second_user_payload["email"],
            "password": second_user_payload["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}