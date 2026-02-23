from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from typing import List
from database import get_session
from models import Bill, User
from auth import get_current_user

router = APIRouter(prefix="/bills", tags=["bills"])

@router.get("/", response_model=List[Bill])
def get_bills(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Bill).where(Bill.user_id == current_user.id)).all()

@router.post("/", response_model=Bill)
def create_bill(bill: Bill, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    bill.id = None # Force DB to generate ID
    bill.user_id = current_user.id
    
    if isinstance(bill.due_date, str):
        bill.due_date = date.fromisoformat(bill.due_date)
        
    session.add(bill)
    session.commit()
    session.refresh(bill)
    return bill

@router.patch("/{bill_id}/pay")
def pay_bill(bill_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    bill = session.get(Bill, bill_id)
    if not bill or bill.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bill not found")
    bill.is_paid = True
    session.add(bill)
    session.commit()
    return {"ok": True}
