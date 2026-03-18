def test_create_team_success(client, auth_headers):
    payload = {
        "name": "Backend Team",
        "description": "API team",
    }

    response = client.post("/api/v1/teams", json=payload, headers=auth_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Backend Team"


def test_creator_becomes_admin(client, auth_headers):
    team_response = client.post(
        "/api/v1/teams",
        json={"name": "Core Team", "description": "desc"},
        headers=auth_headers,
    )
    team_id = team_response.json()["id"]

    members_response = client.get(f"/api/v1/teams/{team_id}/members", headers=auth_headers)
    assert members_response.status_code == 200

    members = members_response.json()
    assert len(members) == 1
    assert members[0]["role"] == "admin"


def test_admin_can_add_member(client, auth_headers, create_second_user):
    team_response = client.post(
        "/api/v1/teams",
        json={"name": "Core Team", "description": "desc"},
        headers=auth_headers,
    )
    team_id = team_response.json()["id"]

    add_response = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": create_second_user["id"], "role": "member"},
        headers=auth_headers,
    )
    assert add_response.status_code == 201
    assert add_response.json()["user_id"] == create_second_user["id"]


def test_non_admin_cannot_add_member(
    client,
    auth_headers,
    second_auth_headers,
    create_second_user,
):
    team_response = client.post(
        "/api/v1/teams",
        json={"name": "Core Team", "description": "desc"},
        headers=auth_headers,
    )
    team_id = team_response.json()["id"]

    client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": create_second_user["id"], "role": "member"},
        headers=auth_headers,
    )

    third_user = client.post(
        "/api/v1/auth/register",
        json={
            "username": "thirduser",
            "email": "thirduser@example.com",
            "password": "strongpass123",
        },
    ).json()

    response = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": third_user["id"], "role": "member"},
        headers=second_auth_headers,
    )
    assert response.status_code == 403


def test_member_can_list_their_teams(client, auth_headers, second_auth_headers, create_second_user):
    team_response = client.post(
        "/api/v1/teams",
        json={"name": "Core Team", "description": "desc"},
        headers=auth_headers,
    )
    team_id = team_response.json()["id"]

    client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": create_second_user["id"], "role": "member"},
        headers=auth_headers,
    )

    response = client.get("/api/v1/teams", headers=second_auth_headers)
    assert response.status_code == 200

    teams = response.json()
    assert len(teams) == 1
    assert teams[0]["id"] == team_id