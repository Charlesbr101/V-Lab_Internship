from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import app.db.crud as crud
import app.schemas as schemas
from app.utils import parse_integrity_error
from app.db.database import SessionLocal
from app.deps import get_current_user_optional

router = APIRouter(prefix="/materials", tags=["Materials"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=schemas.Pagination[schemas.Material])
def read_materials(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
    title: str = Query(None, description="Filter by title"),
    author_name: str = Query(None, description="Filter by author name"),
    description: str = Query(None, description="Filter by description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
):
    items, total = crud.get_materials(db, current_user, title=title, author_name=author_name, description=description, page=page, page_size=page_size)
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


@router.get("/{material_id}", response_model=schemas.Material)
def read_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    db_material = crud.get_material(db, material_id)
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    # If not published, only owner or root may view
    if db_material.status != "published":
        if current_user is None or (db_material.user_id != current_user.id and not getattr(current_user, "is_root", False)):
            raise HTTPException(status_code=403, detail="Not allowed to view this material")
    return db_material
