from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Query, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user
from app.utils import parse_integrity_error

router = APIRouter(prefix="/authors", tags=["Authors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=schemas.Pagination[schemas.Author], responses=schemas.HTTP_ERROR_RESPONSES)
def read_authors(response: Response, request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    items, total = crud.get_authors(db, page=page, page_size=page_size)
    last_page = max(1, (total + page_size - 1) // page_size)
    def _make_url(p: int):
        return str(request.url.replace_query_params(page=p, page_size=page_size))
    links = {
        "first": _make_url(1),
        "prev": _make_url(page - 1) if page > 1 else None,
        "next": _make_url(page + 1) if page < last_page else None,
        "last": _make_url(last_page),
    }
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "links": links,
    }


@router.get("/{author_id}", response_model=schemas.Author, responses=schemas.HTTP_ERROR_RESPONSES)
def read_author(author_id: int, db: Session = Depends(get_db)):
    db_author = crud.get_author(db, author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author

# Person authors
@router.get("/persons", response_model=schemas.Pagination[schemas.AuthorPerson], responses=schemas.HTTP_ERROR_RESPONSES)
def read_person_authors(response: Response, request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    items, total = crud.get_person_authors(db, page=page, page_size=page_size)
    last_page = max(1, (total + page_size - 1) // page_size)
    def _make_url(p: int):
        return str(request.url.replace_query_params(page=p, page_size=page_size))
    links = {
        "first": _make_url(1),
        "prev": _make_url(page - 1) if page > 1 else None,
        "next": _make_url(page + 1) if page < last_page else None,
        "last": _make_url(last_page),
    }
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "links": links,
    }


@router.get("/persons/{person_id}", response_model=schemas.AuthorPerson, responses=schemas.HTTP_ERROR_RESPONSES)
def read_person_author(person_id: int, db: Session = Depends(get_db)):
    db_person = crud.get_person_author(db, person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person author not found")
    return db_person


@router.post("/persons", response_model=schemas.AuthorPerson, status_code=status.HTTP_201_CREATED, responses=schemas.HTTP_ERROR_RESPONSES)
def create_person_author(author: schemas.AuthorPersonCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_person_author(db, author)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


# Institution authors
@router.get("/institutions", response_model=schemas.Pagination[schemas.AuthorInstitution], responses=schemas.HTTP_ERROR_RESPONSES)
def read_institution_authors(response: Response, request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    items, total = crud.get_institution_authors(db, page=page, page_size=page_size)
    last_page = max(1, (total + page_size - 1) // page_size)
    def _make_url(p: int):
        return str(request.url.replace_query_params(page=p, page_size=page_size))
    links = {
        "first": _make_url(1),
        "prev": _make_url(page - 1) if page > 1 else None,
        "next": _make_url(page + 1) if page < last_page else None,
        "last": _make_url(last_page),
    }
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "links": links,
    }


@router.get("/institutions/{institution_id}", response_model=schemas.AuthorInstitution, responses=schemas.HTTP_ERROR_RESPONSES)
def read_institution_author(institution_id: int, db: Session = Depends(get_db)):
    db_inst = crud.get_institution_author(db, institution_id)
    if db_inst is None:
        raise HTTPException(status_code=404, detail="Institution author not found")
    return db_inst


@router.post("/institutions", response_model=schemas.AuthorInstitution, status_code=status.HTTP_201_CREATED, responses=schemas.HTTP_ERROR_RESPONSES)
def create_institution_author(author: schemas.AuthorInstitutionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_institution_author(db, author)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))
