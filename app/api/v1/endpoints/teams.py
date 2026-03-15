from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.team import TeamCreate, TeamMemberAdd, TeamMemberResponse, TeamResponse
from app.services.team_service import (
    add_member_to_team,
    create_team_with_creator_as_admin,
    delete_team_for_admin,
    get_team_for_member_or_404,
    list_current_user_teams,
    list_members_for_team,
    remove_member_from_team,
)

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team_endpoint(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_team_with_creator_as_admin(
        db,
        team_in=team_in,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[TeamResponse],
    status_code=status.HTTP_200_OK,
)
def list_teams_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_current_user_teams(db, current_user=current_user)


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
)
def get_team_endpoint(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_team_for_member_or_404(db, team_id=team_id, current_user=current_user)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_team_endpoint(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_team_for_admin(db, team_id=team_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_team_member_endpoint(
    team_id: int,
    member_in: TeamMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_member_to_team(
        db,
        team_id=team_id,
        user_id=member_in.user_id,
        role=member_in.role,
        current_user=current_user,
    )


@router.get(
    "/{team_id}/members",
    response_model=list[TeamMemberResponse],
    status_code=status.HTTP_200_OK,
)
def list_team_members_endpoint(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_members_for_team(db, team_id=team_id, current_user=current_user)


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_team_member_endpoint(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    remove_member_from_team(
        db,
        team_id=team_id,
        user_id=user_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)