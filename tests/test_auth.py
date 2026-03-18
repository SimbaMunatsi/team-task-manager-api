def test_register_user_success(client, user_payload):
    response = client.post("/api/v1/auth/register", json=user_payload)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == user_payload["username"]
    assert data["email"] == user_payload["email"]
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_email_fails(client, user_payload):
    response1 = client.post("/api/v1/auth/register", json=user_payload)
    assert response1.status_code == 201

    duplicate_payload = {
        "username": "anotheruser",
        "email": user_payload["email"],
        "password": "strongpass123",
    }
    response2 = client.post("/api/v1/auth/register", json=duplicate_payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email is already registered."


def test_register_duplicate_username_fails(client, user_payload):
    response1 = client.post("/api/v1/auth/register", json=user_payload)
    assert response1.status_code == 201

    duplicate_payload = {
        "username": user_payload["username"],
        "email": "another@example.com",
        "password": "strongpass123",
    }
    response2 = client.post("/api/v1/auth/register", json=duplicate_payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Username is already taken."


def test_login_success(client, create_user, user_payload):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_payload["email"],
            "password": user_payload["password"],
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, create_user, user_payload):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_payload["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "missing@example.com",
            "password": "strongpass123",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."