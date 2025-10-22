from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user

router = APIRouter(prefix="/materials/books", tags=["materials"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Book])
def read_books(db: Session = Depends(get_db)):
    return crud.get_books(db)


@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.create_book(db, book)
