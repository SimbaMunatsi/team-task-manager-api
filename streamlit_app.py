import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv("STREAMLIT_API_BASE_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(
    page_title="Team Task Manager",
    page_icon="✅",
    layout="wide",
)

# =========================================================
# Session state defaults
# =========================================================
DEFAULTS = {
    "token": None,
    "current_user": None,
    "loaded_tasks": [],
    "loaded_teams": [],
    "loaded_team_members": [],
    "loaded_comments": [],
    "selected_task_id": None,
    "selected_team_id": None,
    "tasks_meta": {"page": 1, "page_size": 10, "total": 0},
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# API helpers
# =========================================================
def auth_headers() -> dict[str, str]:
    if not st.session_state.token:
        return {}
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_request(
    method: str,
    endpoint: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    auth: bool = False,
) -> requests.Response:
    url = f"{API_BASE_URL}{endpoint}"
    headers: dict[str, str] = {}

    if auth:
        headers.update(auth_headers())

    return requests.request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        params=params,
        timeout=20,
    )


def parse_response(response: requests.Response) -> Any:
    try:
        return response.json()
    except Exception:
        return None


def handle_response(response: requests.Response, success_message: str | None = None) -> Any:
    data = parse_response(response)

    if response.ok:
        if success_message:
            st.success(success_message)
        return data

    detail = "Request failed."
    if isinstance(data, dict) and "detail" in data:
        detail = str(data["detail"])
    elif data is not None:
        detail = str(data)

    st.error(f"{response.status_code}: {detail}")
    return None


# =========================================================
# Auth helpers
# =========================================================
def refresh_current_user() -> None:
    if not st.session_state.token:
        st.session_state.current_user = None
        return

    response = api_request("GET", "/users/me", auth=True)
    data = parse_response(response)

    if response.ok and isinstance(data, dict):
        st.session_state.current_user = data
    else:
        st.session_state.token = None
        st.session_state.current_user = None


def login_user(email: str, password: str) -> None:
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={
            "username": email,
            "password": password,
        },
        timeout=20,
    )

    data = handle_response(response)
    if response.ok and isinstance(data, dict):
        st.session_state.token = data["access_token"]
        refresh_current_user()
        st.success("Logged in successfully.")
        st.rerun()


def register_user(username: str, email: str, password: str) -> None:
    response = api_request(
        "POST",
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    handle_response(response, "Registration successful. You can now log in.")


def logout_user() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.success("Logged out.")
    st.rerun()


# =========================================================
# Utility helpers
# =========================================================
def safe_int(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def tasks_to_dataframe(tasks: list[dict[str, Any]]) -> pd.DataFrame:
    if not tasks:
        return pd.DataFrame()

    rows = []
    for task in tasks:
        rows.append(
            {
                "ID": task["id"],
                "Title": task["title"],
                "Status": task["status"],
                "Priority": task["priority"],
                "Due Date": task.get("due_date"),
                "Team ID": task.get("team_id"),
                "Assigned To": task.get("assigned_to"),
                "Created By": task["created_by"],
            }
        )
    return pd.DataFrame(rows)


def teams_to_dataframe(teams: list[dict[str, Any]]) -> pd.DataFrame:
    if not teams:
        return pd.DataFrame()

    rows = []
    for team in teams:
        rows.append(
            {
                "ID": team["id"],
                "Name": team["name"],
                "Description": team.get("description"),
                "Created By": team["created_by"],
                "Created At": team["created_at"],
            }
        )
    return pd.DataFrame(rows)


def members_to_dataframe(members: list[dict[str, Any]]) -> pd.DataFrame:
    if not members:
        return pd.DataFrame()

    rows = []
    for member in members:
        rows.append(
            {
                "Membership ID": member["id"],
                "Team ID": member["team_id"],
                "User ID": member["user_id"],
                "Role": member["role"],
                "Joined At": member["joined_at"],
            }
        )
    return pd.DataFrame(rows)


def comments_to_dataframe(comments: list[dict[str, Any]]) -> pd.DataFrame:
    if not comments:
        return pd.DataFrame()

    rows = []
    for comment in comments:
        rows.append(
            {
                "Comment ID": comment["id"],
                "Task ID": comment["task_id"],
                "User ID": comment["user_id"],
                "Content": comment["content"],
                "Created At": comment["created_at"],
            }
        )
    return pd.DataFrame(rows)


# =========================================================
# Data loading
# =========================================================
def load_tasks(
    *,
    page: int = 1,
    page_size: int = 10,
    status: str = "",
    priority: str = "",
    search: str = "",
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> None:
    params: dict[str, Any] = {
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if search.strip():
        params["search"] = search.strip()

    response = api_request("GET", "/tasks", params=params, auth=True)
    data = handle_response(response)

    if response.ok and isinstance(data, dict):
        st.session_state.loaded_tasks = data.get("items", [])
        st.session_state.tasks_meta = {
            "page": data.get("page", 1),
            "page_size": data.get("page_size", 10),
            "total": data.get("total", 0),
        }

        if st.session_state.loaded_tasks and st.session_state.selected_task_id is None:
            st.session_state.selected_task_id = st.session_state.loaded_tasks[0]["id"]


def load_teams() -> None:
    response = api_request("GET", "/teams", auth=True)
    data = handle_response(response)

    if response.ok and isinstance(data, list):
        st.session_state.loaded_teams = data
        if st.session_state.loaded_teams and st.session_state.selected_team_id is None:
            st.session_state.selected_team_id = st.session_state.loaded_teams[0]["id"]


def load_team_members(team_id: int) -> None:
    response = api_request("GET", f"/teams/{team_id}/members", auth=True)
    data = handle_response(response)

    if response.ok and isinstance(data, list):
        st.session_state.loaded_team_members = data
        st.session_state.selected_team_id = team_id


def load_comments(task_id: int) -> None:
    response = api_request("GET", f"/tasks/{task_id}/comments", auth=True)
    data = handle_response(response)

    if response.ok and isinstance(data, list):
        st.session_state.loaded_comments = data
        st.session_state.selected_task_id = task_id


def get_selected_task() -> dict[str, Any] | None:
    for task in st.session_state.loaded_tasks:
        if task["id"] == st.session_state.selected_task_id:
            return task
    return None


def get_selected_team() -> dict[str, Any] | None:
    for team in st.session_state.loaded_teams:
        if team["id"] == st.session_state.selected_team_id:
            return team
    return None


# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("✅ Team Task Manager")
st.sidebar.caption("Premium Streamlit dashboard for your FastAPI backend")
st.sidebar.write(f"Backend: `{API_BASE_URL}`")

if st.session_state.token and st.session_state.current_user is None:
    refresh_current_user()

if st.session_state.current_user:
    st.sidebar.success(f"Logged in as {st.session_state.current_user['username']}")
    st.sidebar.write(f"Email: {st.session_state.current_user['email']}")
    if st.sidebar.button("Logout", use_container_width=True):
        logout_user()
else:
    auth_mode = st.sidebar.radio("Account", ["Login", "Register"], horizontal=True)

    if auth_mode == "Login":
        with st.sidebar.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                login_user(email, password)
    else:
        with st.sidebar.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register", use_container_width=True)
            if submitted:
                register_user(username, email, password)

# =========================================================
# Guard
# =========================================================
st.title("Team Task Manager Dashboard")
st.caption("A richer demo interface for tasks, teams, members, and comments")

if not st.session_state.token:
    st.info("Log in or register from the sidebar to continue.")
    st.stop()

# =========================================================
# Top metrics
# =========================================================
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("User", st.session_state.current_user["username"])
with m2:
    st.metric("User ID", st.session_state.current_user["id"])
with m3:
    st.metric("Loaded Tasks", len(st.session_state.loaded_tasks))
with m4:
    st.metric("Loaded Teams", len(st.session_state.loaded_teams))

st.divider()

# =========================================================
# Tabs
# =========================================================
tab_dashboard, tab_tasks, tab_task_actions, tab_teams, tab_team_actions, tab_comments = st.tabs(
    [
        "Dashboard",
        "Tasks",
        "Task Actions",
        "Teams",
        "Team Actions",
        "Comments",
    ]
)

# =========================================================
# Dashboard
# =========================================================
with tab_dashboard:
    st.subheader("Overview")

    left, right = st.columns([2, 1])

    with left:
        st.markdown("### Current User")
        st.json(st.session_state.current_user)

    with right:
        st.markdown("### Quick Refresh")
        if st.button("Refresh Tasks", use_container_width=True):
            load_tasks()

        if st.button("Refresh Teams", use_container_width=True):
            load_teams()

        st.markdown("### Demo Flow")
        st.info(
            "1. Create a team\n"
            "2. Add a member\n"
            "3. Create a team task\n"
            "4. Assign it\n"
            "5. Add comments\n"
            "6. Show edit/delete actions"
        )

    if st.session_state.loaded_tasks:
        st.markdown("### Latest Tasks")
        st.dataframe(tasks_to_dataframe(st.session_state.loaded_tasks), use_container_width=True)

    if st.session_state.loaded_teams:
        st.markdown("### Latest Teams")
        st.dataframe(teams_to_dataframe(st.session_state.loaded_teams), use_container_width=True)

# =========================================================
# Tasks tab
# =========================================================
with tab_tasks:
    st.subheader("Task Explorer")

    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        status_filter = st.selectbox("Status", ["", "todo", "in_progress", "done"])
    with f2:
        priority_filter = st.selectbox("Priority", ["", "low", "medium", "high"])
    with f3:
        sort_by = st.selectbox("Sort By", ["created_at", "due_date", "priority"])
    with f4:
        sort_order = st.selectbox("Sort Order", ["desc", "asc"])
    with f5:
        page_size = st.selectbox("Page Size", [5, 10, 20, 50], index=1)

    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("Search tasks")
    with c2:
        page = st.number_input("Page", min_value=1, value=1, step=1)

    if st.button("Load Tasks", use_container_width=True):
        load_tasks(
            page=int(page),
            page_size=int(page_size),
            status=status_filter,
            priority=priority_filter,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    tasks = st.session_state.loaded_tasks
    meta = st.session_state.tasks_meta

    a, b, c = st.columns(3)
    with a:
        st.metric("Visible Tasks", len(tasks))
    with b:
        st.metric("Total Matching", meta.get("total", 0))
    with c:
        st.metric("Current Page", meta.get("page", 1))

    if tasks:
        st.dataframe(tasks_to_dataframe(tasks), use_container_width=True)

        task_ids = [task["id"] for task in tasks]
        selected_task_id = st.selectbox(
            "Select Task",
            options=task_ids,
            index=task_ids.index(st.session_state.selected_task_id) if st.session_state.selected_task_id in task_ids else 0,
            format_func=lambda task_id: next(
                (f"#{task['id']} - {task['title']}" for task in tasks if task["id"] == task_id),
                str(task_id),
            ),
        )
        st.session_state.selected_task_id = selected_task_id

        selected_task = get_selected_task()
        if selected_task:
            with st.container(border=True):
                st.markdown(f"#### {selected_task['title']}")
                st.write(selected_task.get("description") or "No description.")
                x1, x2, x3, x4 = st.columns(4)
                with x1:
                    st.write(f"**Status:** {selected_task['status']}")
                with x2:
                    st.write(f"**Priority:** {selected_task['priority']}")
                with x3:
                    st.write(f"**Team ID:** {selected_task.get('team_id')}")
                with x4:
                    st.write(f"**Assigned To:** {selected_task.get('assigned_to')}")
                st.caption(f"Created at: {selected_task['created_at']}")
    else:
        st.info("Load tasks to begin.")

# =========================================================
# Task Actions
# =========================================================
with tab_task_actions:
    st.subheader("Create / Update / Delete Tasks")

    create_col, edit_col = st.columns(2)

    with create_col:
        st.markdown("### Create Task")
        with st.form("create_task_form"):
            title = st.text_input("Title")
            description = st.text_area("Description")
            col1, col2, col3 = st.columns(3)
            with col1:
                status = st.selectbox("Status", ["todo", "in_progress", "done"], key="create_status")
            with col2:
                priority = st.selectbox("Priority", ["low", "medium", "high"], index=1, key="create_priority")
            with col3:
                due_date = st.date_input("Due Date", value=None, key="create_due_date")

            team_id_raw = st.text_input("Team ID (optional)", key="create_team_id")
            assigned_to_raw = st.text_input("Assigned To User ID (optional)", key="create_assigned_to")

            submitted = st.form_submit_button("Create Task", use_container_width=True)

            if submitted:
                team_id = safe_int(team_id_raw)
                assigned_to = safe_int(assigned_to_raw)

                if team_id_raw.strip() and team_id is None:
                    st.error("Team ID must be a valid integer.")
                elif assigned_to_raw.strip() and assigned_to is None:
                    st.error("Assigned To must be a valid integer.")
                else:
                    payload = {
                        "title": title,
                        "description": description or None,
                        "status": status,
                        "priority": priority,
                        "due_date": str(due_date) if due_date else None,
                        "team_id": team_id,
                        "assigned_to": assigned_to,
                    }
                    response = api_request("POST", "/tasks", json=payload, auth=True)
                    data = handle_response(response, "Task created successfully.")
                    if response.ok and isinstance(data, dict):
                        st.session_state.selected_task_id = data["id"]
                        load_tasks()

    with edit_col:
        st.markdown("### Update / Delete Selected Task")

        selected_task = get_selected_task()
        if not selected_task:
            st.info("Load tasks and select one first.")
        else:
            st.write(f"Editing task **#{selected_task['id']} - {selected_task['title']}**")

            with st.form("edit_task_form"):
                edit_title = st.text_input("Title", value=selected_task["title"])
                edit_description = st.text_area("Description", value=selected_task.get("description") or "")
                e1, e2, e3 = st.columns(3)
                with e1:
                    edit_status = st.selectbox(
                        "Status",
                        ["todo", "in_progress", "done"],
                        index=["todo", "in_progress", "done"].index(selected_task["status"]),
                    )
                with e2:
                    edit_priority = st.selectbox(
                        "Priority",
                        ["low", "medium", "high"],
                        index=["low", "medium", "high"].index(selected_task["priority"]),
                    )
                with e3:
                    current_due = selected_task.get("due_date")
                    edit_due_date = st.text_input("Due Date (YYYY-MM-DD or blank)", value=current_due or "")

                edit_assigned_to = st.text_input(
                    "Assigned To User ID (optional)",
                    value=str(selected_task["assigned_to"]) if selected_task.get("assigned_to") is not None else "",
                )

                submitted_update = st.form_submit_button("Update Task", use_container_width=True)

                if submitted_update:
                    assigned_to = safe_int(edit_assigned_to)
                    if edit_assigned_to.strip() and assigned_to is None:
                        st.error("Assigned To must be a valid integer.")
                    else:
                        payload = {
                            "title": edit_title,
                            "description": edit_description or None,
                            "status": edit_status,
                            "priority": edit_priority,
                            "due_date": edit_due_date.strip() or None,
                            "assigned_to": assigned_to,
                        }
                        response = api_request(
                            "PATCH",
                            f"/tasks/{selected_task['id']}",
                            json=payload,
                            auth=True,
                        )
                        data = handle_response(response, "Task updated successfully.")
                        if response.ok and isinstance(data, dict):
                            load_tasks()

            if st.button("Delete Selected Task", use_container_width=True, type="primary"):
                response = api_request(
                    "DELETE",
                    f"/tasks/{selected_task['id']}",
                    auth=True,
                )
                if response.status_code == 204:
                    st.success("Task deleted successfully.")
                    st.session_state.selected_task_id = None
                    load_tasks()
                else:
                    handle_response(response)

# =========================================================
# Teams tab
# =========================================================
with tab_teams:
    st.subheader("Teams")

    if st.button("Load My Teams", use_container_width=True):
        load_teams()

    teams = st.session_state.loaded_teams
    if teams:
        st.dataframe(teams_to_dataframe(teams), use_container_width=True)

        team_ids = [team["id"] for team in teams]
        selected_team_id = st.selectbox(
            "Select Team",
            options=team_ids,
            index=team_ids.index(st.session_state.selected_team_id) if st.session_state.selected_team_id in team_ids else 0,
            format_func=lambda team_id: next(
                (f"#{team['id']} - {team['name']}" for team in teams if team["id"] == team_id),
                str(team_id),
            ),
        )
        st.session_state.selected_team_id = selected_team_id

        selected_team = get_selected_team()
        if selected_team:
            with st.container(border=True):
                st.markdown(f"#### {selected_team['name']}")
                st.write(selected_team.get("description") or "No description.")
                st.write(f"**Created By:** {selected_team['created_by']}")
                st.caption(f"Created at: {selected_team['created_at']}")
    else:
        st.info("Load teams to begin.")

# =========================================================
# Team Actions
# =========================================================
with tab_team_actions:
    st.subheader("Create Team / Manage Members")

    left, right = st.columns(2)

    with left:
        st.markdown("### Create Team")
        with st.form("create_team_form"):
            name = st.text_input("Team Name")
            description = st.text_area("Description")
            submitted = st.form_submit_button("Create Team", use_container_width=True)

            if submitted:
                payload = {"name": name, "description": description or None}
                response = api_request("POST", "/teams", json=payload, auth=True)
                data = handle_response(response, "Team created successfully.")
                if response.ok and isinstance(data, dict):
                    st.session_state.selected_team_id = data["id"]
                    load_teams()

    with right:
        st.markdown("### Manage Members")

        selected_team = get_selected_team()
        if not selected_team:
            st.info("Load and select a team first.")
        else:
            st.write(f"Managing members for **#{selected_team['id']} - {selected_team['name']}**")

            if st.button("Load Members", use_container_width=True):
                load_team_members(selected_team["id"])

            if st.session_state.loaded_team_members:
                st.dataframe(
                    members_to_dataframe(st.session_state.loaded_team_members),
                    use_container_width=True,
                )

            with st.form("add_member_form"):
                add_user_id_raw = st.text_input("User ID to Add")
                add_role = st.selectbox("Role", ["member", "admin"])
                add_submitted = st.form_submit_button("Add Member", use_container_width=True)

                if add_submitted:
                    add_user_id = safe_int(add_user_id_raw)
                    if add_user_id is None:
                        st.error("User ID must be a valid integer.")
                    else:
                        payload = {
                            "user_id": add_user_id,
                            "role": add_role,
                        }
                        response = api_request(
                            "POST",
                            f"/teams/{selected_team['id']}/members",
                            json=payload,
                            auth=True,
                        )
                        data = handle_response(response, "Member added successfully.")
                        if response.ok and isinstance(data, dict):
                            load_team_members(selected_team["id"])

            remove_user_id_raw = st.text_input("User ID to Remove")
            if st.button("Remove Member", use_container_width=True):
                remove_user_id = safe_int(remove_user_id_raw)
                if remove_user_id is None:
                    st.error("User ID must be a valid integer.")
                else:
                    response = api_request(
                        "DELETE",
                        f"/teams/{selected_team['id']}/members/{remove_user_id}",
                        auth=True,
                    )
                    if response.status_code == 204:
                        st.success("Member removed successfully.")
                        load_team_members(selected_team["id"])
                    else:
                        handle_response(response)

# =========================================================
# Comments
# =========================================================
with tab_comments:
    st.subheader("Comments for Selected Task")

    selected_task = get_selected_task()
    if not selected_task:
        st.info("Load and select a task first.")
    else:
        st.write(f"Working with comments for **#{selected_task['id']} - {selected_task['title']}**")

        top_left, top_right = st.columns(2)

        with top_left:
            if st.button("Load Comments", use_container_width=True):
                load_comments(selected_task["id"])

        with top_right:
            st.metric("Loaded Comments", len(st.session_state.loaded_comments))

        if st.session_state.loaded_comments:
            st.dataframe(
                comments_to_dataframe(st.session_state.loaded_comments),
                use_container_width=True,
            )

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Add Comment")
            with st.form("add_comment_form"):
                comment_content = st.text_area("Comment Content")
                submitted_comment = st.form_submit_button("Add Comment", use_container_width=True)

                if submitted_comment:
                    if not comment_content.strip():
                        st.error("Comment content is required.")
                    else:
                        payload = {"content": comment_content.strip()}
                        response = api_request(
                            "POST",
                            f"/tasks/{selected_task['id']}/comments",
                            json=payload,
                            auth=True,
                        )
                        data = handle_response(response, "Comment added successfully.")
                        if response.ok and isinstance(data, dict):
                            load_comments(selected_task["id"])

        with c2:
            st.markdown("### Edit / Delete Comment")

            comments = st.session_state.loaded_comments
            if not comments:
                st.info("Load comments first.")
            else:
                comment_ids = [comment["id"] for comment in comments]
                selected_comment_id = st.selectbox(
                    "Select Comment",
                    options=comment_ids,
                    format_func=lambda comment_id: next(
                        (
                            f"#{comment['id']} by user {comment['user_id']}"
                            for comment in comments
                            if comment["id"] == comment_id
                        ),
                        str(comment_id),
                    ),
                )

                selected_comment = next(
                    (comment for comment in comments if comment["id"] == selected_comment_id),
                    None,
                )

                if selected_comment:
                    with st.form("edit_comment_form"):
                        edit_comment_content = st.text_area(
                            "Comment Content",
                            value=selected_comment["content"],
                        )
                        submitted_edit = st.form_submit_button("Update Comment", use_container_width=True)

                        if submitted_edit:
                            payload = {"content": edit_comment_content.strip()}
                            response = api_request(
                                "PATCH",
                                f"/comments/{selected_comment['id']}",
                                json=payload,
                                auth=True,
                            )
                            data = handle_response(response, "Comment updated successfully.")
                            if response.ok and isinstance(data, dict):
                                load_comments(selected_task["id"])

                    if st.button("Delete Comment", use_container_width=True):
                        response = api_request(
                            "DELETE",
                            f"/comments/{selected_comment['id']}",
                            auth=True,
                        )
                        if response.status_code == 204:
                            st.success("Comment deleted successfully.")
                            load_comments(selected_task["id"])
                        else:
                            handle_response(response)