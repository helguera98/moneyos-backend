from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from datetime import timedelta
from typing import Optional, List
from pydantic import BaseModel
from database import create_db_and_tables, get_session
from models import User
from auth import (
    verify_password,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from routers import categories, transactions, bills, loans, analytics

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

app = FastAPI(title="App Finance API", version="1.0.0")

# CORS Configuration - Open for production/Vercel connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log incoming request
    print(f"[BACKEND] {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        print(f"[BACKEND] Response status: {response.status_code}")
        return response
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"[BACKEND] CRITICAL ERROR: {err_msg}")
        # Return a JSON response so the browser doesn't get a CORS error on a raw 500
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "message": str(e), "traceback": err_msg},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        )

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Registration Endpoint
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    email = user_data.email
    password = user_data.password
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
        
    user_exists = session.exec(select(User).where(User.email == email)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=user_data.full_name
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

# Login Endpoint
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Include Routers
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(bills.router)
app.include_router(loans.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to App Finance API - Obsidian Gold Edition"}
