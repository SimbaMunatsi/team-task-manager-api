from datetime import date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskPriority, TaskStatus
from app.models.team_member import TeamMember
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, *, task_in: TaskCreate, created_by: int) -> Task:
    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        created_by=created_by,
        team_id=task_in.team_id,
        assigned_to=task_in.assigned_to,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: int) -> Task | None:
    statement = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None),
    )
    return db.execute(statement).scalar_one_or_none()


def get_tasks_visible_to_user(
    db: Session,
    *,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    due_date_from: date | None = None,
    due_date_to: date | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Task], int]:
    base_filters = [Task.deleted_at.is_(None)]

    visibility_filter = or_(
        Task.created_by == user_id,
        Task.team_id.in_(
            select(TeamMember.team_id).where(TeamMember.user_id == user_id)
        ),
    )

    filters = [*base_filters, visibility_filter]

    if status is not None:
        filters.append(Task.status == status)

    if priority is not None:
        filters.append(Task.priority == priority)

    if due_date_from is not None:
        filters.append(Task.due_date >= due_date_from)

    if due_date_to is not None:
        filters.append(Task.due_date <= due_date_to)

    if search:
        search_term = f"%{search.strip()}%"
        filters.append(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
            )
        )

    count_statement = select(func.count()).select_from(Task).where(*filters)
    total = db.execute(count_statement).scalar_one()

    sort_column_map = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
    }
    sort_column = sort_column_map.get(sort_by, Task.created_at)

    order_clause = sort_column.asc() if sort_order == "asc" else sort_column.desc()

    statement = (
        select(Task)
        .where(*filters)
        .order_by(order_clause, Task.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    items = list(db.execute(statement).scalars().all())
    return items, total


def update_task(db: Session, *, task: Task, task_in: TaskUpdate) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def soft_delete_task(db: Session, *, task: Task) -> Task:
    task.deleted_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task