# src/merchants/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

# Gunakan URL SYNC yang sudah diturunkan dari config (psycopg2/psycopg)
SYNC_URL = settings.database_url_sync

# future=True disarankan di SQLAlchemy 2.x
engine = create_engine(SYNC_URL, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
