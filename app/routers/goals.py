from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import SavingGoal, User
from app.schemas import (
    SavingGoalCreate,
    SavingGoalResponse,
    SavingGoalUpdate,
)

router = APIRouter(
    prefix="/goals",
    tags=["Saving Goals"],
)


@router.post(
    "/",
    response_model=SavingGoalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_goal(
    goal_data: SavingGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavingGoal:
    """Create a new saving goal for the current user."""
    new_goal = SavingGoal(
        title=goal_data.title,
        target_amount=goal_data.target_amount,
        current_amount=goal_data.current_amount,
        deadline=goal_data.deadline,
        user_id=current_user.id,
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal


@router.get(
    "/",
    response_model=list[SavingGoalResponse],
    status_code=status.HTTP_200_OK,
)
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavingGoal]:
    """Return all saving goals of the current user."""
    goals = (
        db.query(SavingGoal)
        .filter(SavingGoal.user_id == current_user.id)
        .all()
    )

    return goals


@router.get(
    "/{goal_id}",
    response_model=SavingGoalResponse,
    status_code=status.HTTP_200_OK,
)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavingGoal:
    """Return one saving goal by id."""
    goal = (
        db.query(SavingGoal)
        .filter(
            SavingGoal.id == goal_id,
            SavingGoal.user_id == current_user.id,
        )
        .first()
    )

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saving goal not found",
        )

    return goal


@router.put(
    "/{goal_id}",
    response_model=SavingGoalResponse,
    status_code=status.HTTP_200_OK,
)
def update_goal(
    goal_id: int,
    goal_data: SavingGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavingGoal:
    """Update one saving goal by id."""
    goal = (
        db.query(SavingGoal)
        .filter(
            SavingGoal.id == goal_id,
            SavingGoal.user_id == current_user.id,
        )
        .first()
    )

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saving goal not found",
        )

    update_data = goal_data.model_dump(exclude_unset=True)

    if "title" in update_data:
        goal.title = update_data["title"]

    if "target_amount" in update_data:
        goal.target_amount = update_data["target_amount"]

    if "current_amount" in update_data:
        goal.current_amount = update_data["current_amount"]

    if "deadline" in update_data:
        goal.deadline = update_data["deadline"]

    db.commit()
    db.refresh(goal)

    return goal


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete one saving goal by id."""
    goal = (
        db.query(SavingGoal)
        .filter(
            SavingGoal.id == goal_id,
            SavingGoal.user_id == current_user.id,
        )
        .first()
    )

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saving goal not found",
        )

    db.delete(goal)
    db.commit()
    