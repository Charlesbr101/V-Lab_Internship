from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.create_user(db, user)
