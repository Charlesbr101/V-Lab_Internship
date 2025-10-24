import pytest
from pydantic import ValidationError

from app.schemas import UserCreate, BookCreate, ArticleCreate, MaterialBase


def test_user_password_min_length():
    with pytest.raises(ValidationError):
        UserCreate.model_validate({"email": "a@b.com", "password": "123"})


def test_book_isbn_validation():
    # invalid ISBN should raise
    with pytest.raises(ValidationError):
        BookCreate.model_validate({
            "title": "Tit",
            "description": "d",
            "status": "published",
            "author_id": 1,
            "isbn": "123",
            "page_count": 10,
        })

    # valid ISBN-13 should pass
    b = BookCreate.model_validate({
        "title": "Tit",
        "description": "d",
        "status": "published",
        "author_id": 1,
        "isbn": "9783161484100",
        "page_count": 10,
    })
    assert b.isbn == "9783161484100"


def test_article_doi_validation():
    with pytest.raises(ValidationError):
        ArticleCreate.model_validate({
            "title": "Art",
            "description": "d",
            "status": "published",
            "author_id": 1,
            "doi": "not-a-doi",
        })


def test_material_status_validation():
    with pytest.raises(ValidationError):
        MaterialBase.model_validate({
            "title": "Mat",
            "description": "d",
            "status": "invalid-status",
            "author_id": 1,
        })
