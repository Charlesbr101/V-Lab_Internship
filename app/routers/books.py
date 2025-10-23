from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Query, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils import parse_integrity_error
import requests
from requests.exceptions import RequestException
from typing import Optional, Dict, Any

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user, get_current_user_optional

router = APIRouter(prefix="/materials/books", tags=["materials"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=schemas.Pagination[schemas.Book])
def read_books(
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
    items, total = crud.get_books(db, current_user, title=title, author_name=author_name, description=description, page=page, page_size=page_size)
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


@router.post("", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Prefer incoming data: if caller provided both title and page_count, skip enrichment
    incoming = book.model_dump()
    has_title = bool(incoming.get("title"))
    has_page_count = bool(incoming.get("page_count"))

    book_data: Dict[str, Any] = incoming.copy()

    if not (has_title and has_page_count):
        # Try to enrich with OpenLibrary data using the ISBN, but only fill missing fields
        isbn_val = incoming.get("isbn")
        if isbn_val:
            try:
                meta = fetch_openlibrary_metadata(isbn_val)
                if meta:
                    # Only set fields that were not provided by caller
                    if not has_title and meta.get("title"):
                        book_data["title"] = meta.get("title")
                    if not has_page_count and meta.get("page_count") is not None:
                        book_data["page_count"] = int(meta.get("page_count"))
            except Exception:
                # enrichment failed; proceed with provided data
                pass

    # Validate merged data and create
    book_obj = schemas.BookCreate.model_validate(book_data)
    try:
        return crud.create_book(db, book_obj, current_user.id)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


def fetch_openlibrary_metadata(isbn: str) -> Optional[Dict[str, Any]]:
    """Query OpenLibrary API and return a dict with possible keys: title, page_count.

    Returns None if no data found or on network error.
    """
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        j = resp.json()
        key = f"ISBN:{isbn}"
        if key not in j:
            return None
        info = j[key]
        result: Dict[str, Any] = {}
        if "title" in info:
            result["title"] = info.get("title")
        if "number_of_pages" in info:
            result["page_count"] = info.get("number_of_pages")
        return result
    except RequestException:
        return None


@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_book = crud.get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if db_book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this book")
    try:
        updated = crud.update_book(db, book_id, book.model_dump())
        return updated
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))


@router.delete("/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_book = crud.get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if db_book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this book")
    try:
        deleted = crud.delete_book(db, book_id)
        return deleted
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=parse_integrity_error(e))
