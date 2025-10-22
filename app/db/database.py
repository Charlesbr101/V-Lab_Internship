from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Use pool_pre_ping to help with MySQL connections that may be closed by the server
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

__all__ = ["engine", "SessionLocal", "Base"]
