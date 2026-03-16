from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment_service import (
    create_comment_for_task,
    delete_comment_for_user,
    list_comments_for_visible_task,
    update_comment_for_user,
)

router = APIRouter(tags=["Comments"])


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment_endpoint(
    task_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_comment_for_task(
        db,
        task_id=task_id,
        comment_in=comment_in,
        current_user=current_user,
    )


@router.get(
    "/tasks/{task_id}/comments",
    response_model=list[CommentResponse],
    status_code=status.HTTP_200_OK,
)
def list_comments_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_comments_for_visible_task(
        db,
        task_id=task_id,
        current_user=current_user,
    )


@router.patch(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def update_comment_endpoint(
    comment_id: int,
    comment_in: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_comment_for_user(
        db,
        comment_id=comment_id,
        comment_in=comment_in,
        current_user=current_user,
    )


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment_endpoint(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_comment_for_user(
        db,
        comment_id=comment_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)