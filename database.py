from sqlmodel import create_engine, SQLModel, Session
import os

# Database Configuration
# Read from environment variable (Railway/Production) or fallback to local
database_url = os.getenv("DATABASE_URL", "sqlite:///./finance.db")

# Ensure SQLite URLs are correctly formatted for SQLModel
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(database_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
