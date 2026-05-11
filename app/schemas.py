"""Pydantic schemas for request and response validation."""

from datetime import date as DateType, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CategoryType(str, Enum):
    """Allowed category types."""

    INCOME = "income"
    EXPENSE = "expense"


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for access token response."""

    access_token: str
    token_type: str


class CategoryBase(BaseModel):
    """Base schema for category data."""

    name: str = Field(min_length=1, max_length=100)
    type: CategoryType


class CategoryCreate(CategoryBase):
    """Schema for category creation."""


class CategoryUpdate(BaseModel):
    """Schema for category update."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    type: CategoryType | None = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    """Base schema for transaction data."""

    amount: float = Field(gt=0)
    description: str | None = Field(default=None, max_length=255)
    date: DateType | None = None
    category_id: int


class TransactionCreate(TransactionBase):
    """Schema for transaction creation."""


class TransactionUpdate(BaseModel):
    """Schema for transaction update."""

    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=255)
    date: DateType | None = None
    category_id: int | None = None


class TransactionResponse(BaseModel):
    """Schema for transaction response."""

    id: int
    amount: float
    description: str | None
    date: DateType
    category_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class SavingGoalBase(BaseModel):
    """Base schema for saving goal data."""

    title: str = Field(min_length=1, max_length=100)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: DateType


class SavingGoalCreate(SavingGoalBase):
    """Schema for saving goal creation."""


class SavingGoalUpdate(BaseModel):
    """Schema for saving goal update."""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    deadline: DateType | None = None


class SavingGoalResponse(SavingGoalBase):
    """Schema for saving goal response."""

    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class SavingsPlanRequest(BaseModel):
    """Schema for savings plan request."""

    monthly_income: float = Field(gt=0)
    target_amount: float = Field(gt=0)
    months: int = Field(gt=0, le=120)


class SavingsPlanResponse(BaseModel):
    """Schema for savings plan response."""

    monthly_saving_required: float
    average_monthly_expenses: float
    free_money: float
    is_goal_realistic: bool
    recommendations: list[str]
