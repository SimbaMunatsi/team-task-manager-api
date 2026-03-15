from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, *, task_in: TaskCreate, created_by: int) -> Task:
    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        created_by=created_by,
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


def get_tasks_by_owner(db: Session, owner_id: int) -> list[Task]:
    statement = (
        select(Task)
        .where(
            Task.created_by == owner_id,
            Task.deleted_at.is_(None),
        )
        .order_by(Task.created_at.desc())
    )
    return list(db.execute(statement).scalars().all())


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