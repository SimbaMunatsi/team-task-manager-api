from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.task import (
    create_task,
    get_task_by_id,
    get_tasks_by_owner,
    soft_delete_task,
    update_task,
)
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskListResponse, TaskUpdate


def create_task_for_user(db: Session, *, task_in: TaskCreate, current_user: User) -> Task:
    return create_task(db, task_in=task_in, created_by=current_user.id)


def list_tasks_for_user(
    db: Session,
    *,
    current_user: User,
    page: int = 1,
    page_size: int = 10,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    due_date_from: date | None = None,
    due_date_to: date | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> TaskListResponse:
    items, total = get_tasks_by_owner(
        db,
        owner_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return TaskListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


def get_user_task_or_404(db: Session, *, task_id: int, current_user: User) -> Task:
    task = get_task_by_id(db, task_id=task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    if task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this task.",
        )

    return task


def update_user_task(
    db: Session,
    *,
    task_id: int,
    task_in: TaskUpdate,
    current_user: User,
) -> Task:
    task = get_user_task_or_404(db, task_id=task_id, current_user=current_user)
    return update_task(db, task=task, task_in=task_in)


def delete_user_task(db: Session, *, task_id: int, current_user: User) -> None:
    task = get_user_task_or_404(db, task_id=task_id, current_user=current_user)
    soft_delete_task(db, task=task)