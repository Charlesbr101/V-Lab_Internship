from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils import parse_integrity_error

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

@router.get("", response_model=schemas.Pagination[schemas.User])
def read_users(response: Response, request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    # Efficient pagination using DB queries
    q = db.query(crud.User)
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(crud.User.id).limit(page_size).offset(offset).all()
    last_page = max(1, (total + page_size - 1) // page_size)
    # build links
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


@router.post("", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_user(db, user)
    except IntegrityError as e:
        # translate DB constraint errors to HTTP 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))
