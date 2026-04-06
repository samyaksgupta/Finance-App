from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, UTC
from enum import Enum

class UserRole(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

# Transaction Schemas
class TransactionBase(BaseModel):
    amount: float = Field(gt=0, description="Amount must be greater than 0")
    type: TransactionType
    category: str
    date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.VIEWER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Summary Schemas
class CategoryBreakdown(BaseModel):
    category: str
    total: float

class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    current_balance: float
    category_breakdown: List[CategoryBreakdown]
    recent_activity: List[Transaction]
