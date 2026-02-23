from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import date
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    
    categories: List["Category"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    bills: List["Bill"] = Relationship(back_populates="user")
    loans: List["Loan"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    icon: str
    color: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    user: Optional[User] = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    description: str
    date: date
    type: TransactionType
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_bill: bool = False
    
    user: Optional[User] = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")

class Bill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    amount: float
    due_date: date
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_paid: bool = False
    frequency: str = "monthly" # monthly, weekly, yearly
    
    user: Optional[User] = Relationship(back_populates="bills")

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lender: str
    amount: float
    remaining_balance: float
    due_date: date
    interest_rate: Optional[float] = 0.0
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    status: str = "active" # active, paid
    
    # New fields
    debt_type: str = "loan" # loan, card
    term_months: Optional[int] = None
    min_payment: Optional[float] = 0.0
    
    user: Optional[User] = Relationship(back_populates="loans")
