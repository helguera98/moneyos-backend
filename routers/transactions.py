from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from typing import List
from database import get_session
from models import Transaction, User
from auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=List[Transaction])
def get_transactions(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Transaction).where(Transaction.user_id == current_user.id)).all()

@router.post("/", response_model=Transaction)
def create_transaction(transaction: Transaction, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    transaction.id = None # Force DB to generate ID
    transaction.user_id = current_user.id
    
    # Force conversion to date if it's a string, to satisfy SQLite requirements
    if isinstance(transaction.date, str):
        transaction.date = date.fromisoformat(transaction.date)
        
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction
