from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from typing import List
from database import get_session
from models import Loan, User, Transaction, TransactionType, Category
from auth import get_current_user

router = APIRouter(prefix="/loans", tags=["loans"])

@router.get("/", response_model=List[Loan])
def get_loans(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Loan).where(Loan.user_id == current_user.id)).all()

@router.post("/", response_model=Loan)
def create_loan(loan: Loan, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    loan.id = None # Force DB to generate ID
    loan.user_id = current_user.id
    
    if isinstance(loan.due_date, str):
        loan.due_date = date.fromisoformat(loan.due_date)
        
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan

@router.delete("/{loan_id}")
def delete_loan(loan_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    loan = session.get(Loan, loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    session.delete(loan)
    session.commit()
    return {"message": "Loan deleted"}

@router.post("/{loan_id}/extra-payment")
def apply_extra_payment(
    loan_id: int, 
    payment_data: dict, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    loan = session.get(Loan, loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    amount = payment_data.get("amount")
    if not amount or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    # Update loan balance
    loan.remaining_balance = max(0, loan.remaining_balance - amount)
    if loan.remaining_balance == 0:
        loan.status = "paid"
    
    # Create transaction for history
    # Find or create a 'Debt Payment' category
    category = session.exec(
        select(Category).where(Category.name == "Debt Payment", Category.user_id == current_user.id)
    ).first()
    
    if not category:
        category = Category(
            name="Debt Payment",
            icon="payments",
            color="#D4AF37", # Gold
            user_id=current_user.id
        )
        session.add(category)
        session.commit()
        session.refresh(category)
    
    transaction = Transaction(
        amount=amount,
        description=f"Extra payment to {loan.lender}",
        date=date.today(),
        type=TransactionType.EXPENSE,
        category_id=category.id,
        user_id=current_user.id
    )
    
    session.add(loan)
    session.add(transaction)
    session.commit()
    session.refresh(loan)
    
    return loan
