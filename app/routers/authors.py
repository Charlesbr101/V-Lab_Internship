from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user
from app.utils import parse_integrity_error

router = APIRouter(prefix="/authors", tags=["authors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=List[schemas.Author])
def read_authors(db: Session = Depends(get_db)):
    return crud.get_authors(db)

# Person authors
@router.get("/persons", response_model=List[schemas.PersonAuthor])
def read_person_authors(db: Session = Depends(get_db)):
    return crud.get_person_authors(db)


@router.post("/persons", response_model=schemas.PersonAuthor, status_code=status.HTTP_201_CREATED)
def create_person_author(author: schemas.PersonAuthorCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_person_author(db, author)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


# Institution authors
@router.get("/institutions", response_model=List[schemas.InstitutionAuthor])
def read_institution_authors(db: Session = Depends(get_db)):
    return crud.get_institution_authors(db)


@router.post("/institutions", response_model=schemas.InstitutionAuthor, status_code=status.HTTP_201_CREATED)
def create_institution_author(author: schemas.InstitutionAuthorCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_institution_author(db, author)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))
