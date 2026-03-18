def create_personal_task(client, auth_headers):
    payload = {
        "title": "Task with comment",
        "description": "desc",
        "status": "todo",
        "priority": "medium",
        "due_date": "2026-03-20",
        "team_id": None,
        "assigned_to": None,
    }
    response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    return response.json()["id"]


def test_create_comment_on_own_task(client, auth_headers):
    task_id = create_personal_task(client, auth_headers)

    response = client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "This is a comment"},
        headers=auth_headers,
    )
    assert response.status_code == 201

    data = response.json()
    assert data["task_id"] == task_id
    assert data["content"] == "This is a comment"


def test_list_comments_for_task(client, auth_headers):
    task_id = create_personal_task(client, auth_headers)

    client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "First comment"},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/tasks/{task_id}/comments", headers=auth_headers)
    assert response.status_code == 200

    comments = response.json()
    assert len(comments) == 1
    assert comments[0]["content"] == "First comment"


def test_comment_owner_can_edit_comment(client, auth_headers):
    task_id = create_personal_task(client, auth_headers)

    create_response = client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "Original comment"},
        headers=auth_headers,
    )
    comment_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/comments/{comment_id}",
        json={"content": "Updated comment"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["content"] == "Updated comment"


def test_comment_owner_can_delete_comment(client, auth_headers):
    task_id = create_personal_task(client, auth_headers)

    create_response = client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "Delete me"},
        headers=auth_headers,
    )
    comment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/comments/{comment_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    list_response = client.get(f"/api/v1/tasks/{task_id}/comments", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_non_owner_cannot_edit_personal_task_comment(
    client,
    auth_headers,
    second_auth_headers,
):
    task_id = create_personal_task(client, auth_headers)

    create_response = client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "Owner comment"},
        headers=auth_headers,
    )
    comment_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/comments/{comment_id}",
        json={"content": "Hack edit"},
        headers=second_auth_headers,
    )
    assert response.status_code == 403

def test_team_admin_can_delete_team_task_comment(
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

    task_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Team task",
            "description": "desc",
            "status": "todo",
            "priority": "medium",
            "due_date": "2026-03-20",
            "team_id": team_id,
            "assigned_to": None,
        },
        headers=auth_headers,
    )
    task_id = task_response.json()["id"]

    comment_response = client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "Member comment"},
        headers=second_auth_headers,
    )
    comment_id = comment_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/comments/{comment_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204    