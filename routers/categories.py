from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Category, User
from auth import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def get_categories(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Category).where(Category.user_id == current_user.id)).all()

@router.post("/", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    category.user_id = current_user.id
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.delete("/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}
