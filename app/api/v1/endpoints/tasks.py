from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import (
    SortByType,
    SortOrderType,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import (
    create_task_for_user,
    delete_user_task,
    get_user_task_or_404,
    list_tasks_for_user,
    update_user_task,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task_for_user(db, task_in=task_in, current_user=current_user)


@router.get(
    "",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
)
def list_tasks_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    due_date_from: date | None = None,
    due_date_to: date | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=255),
    sort_by: SortByType = "created_at",
    sort_order: SortOrderType = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_tasks_for_user(
        db,
        current_user=current_user,
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


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def get_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_task_or_404(db, task_id=task_id, current_user=current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def update_task_endpoint(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_task(
        db,
        task_id=task_id,
        task_in=task_in,
        current_user=current_user,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_user_task(db, task_id=task_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)