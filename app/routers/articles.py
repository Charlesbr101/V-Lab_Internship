from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils import parse_integrity_error

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user, get_current_user_optional

router = APIRouter(prefix="/materials/articles", tags=["materials"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Article])
def read_articles(db: Session = Depends(get_db), current_user=Depends(get_current_user_optional)):
    return crud.get_articles(db, current_user)


@router.post("/", response_model=schemas.Article, status_code=status.HTTP_201_CREATED)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_article(db, article)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


@router.put("/{article_id}", response_model=schemas.Article)
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


@router.delete("/{article_id}", response_model=schemas.Article)
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
