def test_get_current_user_success(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["username"] == "testuser"


def test_get_current_user_without_token_fails(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_current_user_with_invalid_token_fails(client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401