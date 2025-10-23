from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils import parse_integrity_error

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=schemas.Pagination[schemas.User], responses=schemas.HTTP_ERROR_RESPONSES)
def read_users(response: Response, request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), current_user=Depends(get_current_user)):
    # Efficient pagination using DB queries
    q = db.query(crud.User)
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(crud.User.id).limit(page_size).offset(offset).all()
    last_page = max(1, (total + page_size - 1) // page_size)
    # build links
    def _make_url(p: int):
        return str(request.url.replace_query_params(page=p, page_size=page_size))

    # Only root may view full user list
    if not getattr(current_user, "is_root", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the root user can view users")

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


@router.get("/{user_id}", response_model=schemas.User, responses=schemas.HTTP_ERROR_RESPONSES)
def read_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Only root may view user details
    if not getattr(current_user, "is_root", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the root user can view users")
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("", response_model=schemas.User, status_code=status.HTTP_201_CREATED, responses=schemas.HTTP_ERROR_RESPONSES)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Only the root user may perform user CRUD operations
    if not getattr(current_user, "is_root", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the root user can manage users")
    try:
        return crud.create_user(db, user)
    except IntegrityError as e:
        # translate DB constraint errors to HTTP 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


@router.put("/{user_id}", response_model=schemas.User, responses=schemas.HTTP_ERROR_RESPONSES)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Only root can update users
    if not getattr(current_user, "is_root", False) and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the root or same user can manage users")
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        updated = crud.update_user(db, user_id, user.model_dump(exclude_none=True))
        return updated
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


@router.delete("/{user_id}", response_model=schemas.User, responses=schemas.HTTP_ERROR_RESPONSES)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Only root can delete users
    if not getattr(current_user, "is_root", False) and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the root or same user can manage users")
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        deleted = crud.delete_user(db, user_id)
        return deleted
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))
