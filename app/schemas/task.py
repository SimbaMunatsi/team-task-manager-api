from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None


class TaskCreate(TaskBase):
    team_id: int | None = None
    assigned_to: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    assigned_to: int | None = None


class TaskResponse(TaskBase):
    id: int
    created_by: int
    team_id: int | None = None
    assigned_to: int | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    page: int
    page_size: int
    total: int


SortByType = Literal["created_at", "due_date", "priority"]
SortOrderType = Literal["asc", "desc"]