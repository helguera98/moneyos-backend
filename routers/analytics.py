from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from database import get_session
from models import Transaction, Category, User
from auth import get_current_user
from datetime import datetime
from typing import Dict, List

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
async def get_financial_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Calculate Total Income, Total Expenses, and Savings Rate for CURRENT USER
    transactions = session.exec(select(Transaction).where(Transaction.user_id == current_user.id)).all()
    
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    # 2. Category Breakdown
    category_summary = []
    categories = session.exec(select(Category).where(Category.user_id == current_user.id)).all()
    for cat in categories:
        cat_expenses = sum(t.amount for t in transactions if t.category_id == cat.id and t.type == "expense")
        if cat_expenses > 0:
            category_summary.append({
                "name": cat.name,
                "amount": cat_expenses,
                "icon": cat.icon,
                "color": cat.color,
                "percentage": (cat_expenses / total_expenses * 100) if total_expenses > 0 else 0
            })
            
    # Sort breakdown by amount descending
    category_summary.sort(key=lambda x: x["amount"], reverse=True)
            
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "savings": savings,
        "savings_rate": round(savings_rate, 2),
        "category_breakdown": category_summary
    }

@router.get("/monthly-trend")
async def get_monthly_trend(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # For now, we still return semi-static data but filtered or contextualized could go here
    # In a real app, we'd aggregate current_user transactions by month
    return [
        {"month": "Jan", "income": 4500, "expenses": 3200},
        {"month": "Feb", "income": 4800, "expenses": 3100},
        {"month": "Mar", "income": 5000, "expenses": 3400}
    ]
