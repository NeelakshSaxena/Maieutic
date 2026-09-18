import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Expect DATABASE_URL (canonical) or POSTGRES_URL (fallback), or default to a local testing sqlite DB
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")

if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./maieutic.db"

# Connect args needed for SQLite, ignored by Postgres
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
