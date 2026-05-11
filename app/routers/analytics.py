"""Analytics routes for budget calculations."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Category, Transaction, User
from app.schemas import SavingsPlanRequest, SavingsPlanResponse
from app.services.analytics_service import generate_savings_plan

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.post(
    "/savings-plan",
    response_model=SavingsPlanResponse,
    status_code=status.HTTP_200_OK,
)
def get_savings_plan(
    plan_data: SavingsPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavingsPlanResponse:
    """
    Generate a savings plan for the current user.

    The plan is based on user's transactions, categories,
    monthly income, target amount and number of months.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    categories = (
        db.query(Category)
        .filter(Category.user_id == current_user.id)
        .all()
    )

    return generate_savings_plan(
        monthly_income=plan_data.monthly_income,
        target_amount=plan_data.target_amount,
        months=plan_data.months,
        transactions=transactions,
        categories=categories,
    )
