def test_create_task_success(client, auth_headers):
    payload = {
        "title": "Test task",
        "description": "Testing task creation",
        "status": "todo",
        "priority": "high",
        "due_date": "2026-03-20",
        "team_id": None,
        "assigned_to": None,
    }

    response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["priority"] == payload["priority"]


def test_list_tasks_returns_paginated_shape(client, auth_headers):
    for i in range(3):
        payload = {
            "title": f"Task {i}",
            "description": "desc",
            "status": "todo",
            "priority": "medium",
            "due_date": "2026-03-20",
            "team_id": None,
            "assigned_to": None,
        }
        client.post("/api/v1/tasks", json=payload, headers=auth_headers)

    response = client.get("/api/v1/tasks?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data
    assert len(data["items"]) == 2
    assert data["total"] == 3


def test_get_task_success(client, auth_headers):
    payload = {
        "title": "Single task",
        "description": "desc",
        "status": "todo",
        "priority": "medium",
        "due_date": "2026-03-20",
        "team_id": None,
        "assigned_to": None,
    }
    create_response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_own_task_success(client, auth_headers):
    payload = {
        "title": "Original task",
        "description": "desc",
        "status": "todo",
        "priority": "medium",
        "due_date": "2026-03-20",
        "team_id": None,
        "assigned_to": None,
    }
    create_response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "done", "priority": "high"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200

    data = update_response.json()
    assert data["status"] == "done"
    assert data["priority"] == "high"


def test_delete_task_soft_delete_success(client, auth_headers):
    payload = {
        "title": "Delete task",
        "description": "desc",
        "status": "todo",
        "priority": "medium",
        "due_date": "2026-03-20",
        "team_id": None,
        "assigned_to": None,
    }
    create_response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_user_cannot_access_other_users_personal_task(
    client,
    auth_headers,
    second_auth_headers,
):
    payload = {
        "title": "Private task",
        "description": "desc",
        "status": "todo",
        "priority": "medium",
        "due_date": "2026-03-20",
        "team_id": None,
        "assigned_to": None,
    }
    create_response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.get(f"/api/v1/tasks/{task_id}", headers=second_auth_headers)
    assert response.status_code == 403


def test_task_search_filtering(client, auth_headers):
    tasks = [
        {
            "title": "Fix login bug",
            "description": "JWT problem",
            "status": "todo",
            "priority": "high",
            "due_date": "2026-03-20",
            "team_id": None,
            "assigned_to": None,
        },
        {
            "title": "Write docs",
            "description": "README update",
            "status": "done",
            "priority": "low",
            "due_date": "2026-03-18",
            "team_id": None,
            "assigned_to": None,
        },
    ]

    for task in tasks:
        client.post("/api/v1/tasks", json=task, headers=auth_headers)

    response = client.get(
        "/api/v1/tasks?status=todo&priority=high&search=login",
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Fix login bug"