from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Query, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils import parse_integrity_error

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user, get_current_user_optional

router = APIRouter(prefix="/materials/articles", tags=["Materials - Articles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=schemas.Pagination[schemas.Article], responses=schemas.HTTP_ERROR_RESPONSES)
def read_articles(
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
    items, total = crud.get_articles(db, current_user, title=title, author_name=author_name, description=description, page=page, page_size=page_size)
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


@router.get("/{article_id}", response_model=schemas.Article, responses=schemas.HTTP_ERROR_RESPONSES)
def read_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    db_article = crud.get_article(db, article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.status != "published":
        if current_user is None or (db_article.user_id != current_user.id and not getattr(current_user, "is_root", False)):
            raise HTTPException(status_code=403, detail="Not allowed to view this article")
    return db_article


@router.post("", response_model=schemas.Article, status_code=status.HTTP_201_CREATED, responses=schemas.HTTP_ERROR_RESPONSES)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_article(db, article, current_user.id)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


@router.put("/{article_id}", response_model=schemas.Article, responses=schemas.HTTP_ERROR_RESPONSES)
def update_article(article_id: int, article: schemas.ArticleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_article = crud.get_article(db, article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this article")
    try:
        updated = crud.update_article(db, article_id, article.model_dump())
        return updated
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


@router.delete("/{article_id}", response_model=schemas.Article, responses=schemas.HTTP_ERROR_RESPONSES)
def delete_article(article_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_article = crud.get_article(db, article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this article")
    try:
        deleted = crud.delete_article(db, article_id)
        return deleted
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))
