from typing import Generator

import app.db.database as db_mod
from app import schemas
from app.db import crud


def make_isbn13(n: int) -> str:
    base = str(978000000000 + n)
    base = base[-12:]
    checksum = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
    check = (10 - (checksum % 10)) % 10
    return base + str(check)


# Tests use the `client` and `db_session` fixtures from tests/conftest.py which
# configure and bind a MySQL test database. No SQLite fallback is used.


def test_books_pagination_http(client, db_session, make_user):
    # client and db_session are provided by fixtures in tests/conftest.py
    # client is a TestClient bound to the test MySQL DB, db_session is a SQLAlchemy session
    session = db_session
    person_s = schemas.AuthorPersonCreate.model_validate({"name": "HTTP Pag Author", "birth_date": "1970-01-01"})
    person = crud.create_person_author(session, person_s)

    # create user via API
    user = make_user("pager_http@example.com", "password")

    # create 15 published books
    for i in range(15):
        book_s = schemas.BookCreate.model_validate({
            "title": f"HTTP Book {i}",
            "description": "desc",
            "status": "published",
            "author_id": person.id,
            "isbn": make_isbn13(i + 1),
            "page_count": 100 + i,
        })
        # create via HTTP so the server sets the user_id correctly
        payload = book_s.model_dump()
        r = client.post("/materials/books", json=payload, auth=(user["email"], "password"))
        assert r.status_code == 201, r.text

    # request page 1
    r = client.get("/materials/books?page=1&page_size=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 15
    assert len(data["items"]) == 10
    assert data["links"]["next"] is not None

    # request page 2
    r2 = client.get("/materials/books?page=2&page_size=10")
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["total"] == 15
    assert len(d2["items"]) == 5


def test_materials_visibility_http(client, db_session, make_user):
    session = db_session

    person_s = schemas.AuthorPersonCreate.model_validate({"name": "HTTP Vis Author", "birth_date": "1975-01-01"})
    person = crud.create_person_author(session, person_s)

    user1 = make_user("hu1@example.com", "password")
    user2 = make_user("hu2@example.com", "password")

    # user1: 3 drafts, 2 published (create via HTTP)
    for i in range(3):
        b = schemas.BookCreate.model_validate({
            "title": f"HU1 Draft {i}",
            "description": "d",
            "status": "draft",
            "author_id": person.id,
            "isbn": make_isbn13(100 + i),
            "page_count": 10,
        })
        r = client.post("/materials/books", json=b.model_dump(), auth=(user1["email"], "password"))
        assert r.status_code == 201, r.text

    for i in range(2):
        b = schemas.BookCreate.model_validate({
            "title": f"HU1 Pub {i}",
            "description": "d",
            "status": "published",
            "author_id": person.id,
            "isbn": make_isbn13(200 + i),
            "page_count": 10,
        })
        r = client.post("/materials/books", json=b.model_dump(), auth=(user1["email"], "password"))
        assert r.status_code == 201, r.text

    # user2: 4 published
    for i in range(4):
        b = schemas.BookCreate.model_validate({
            "title": f"HU2 Pub {i}",
            "description": "d",
            "status": "published",
            "author_id": person.id,
            "isbn": make_isbn13(300 + i),
            "page_count": 10,
        })
        r = client.post("/materials/books", json=b.model_dump(), auth=(user2["email"], "password"))
        assert r.status_code == 201, r.text

    # anonymous: only published (2 + 4 = 6)
    r = client.get("/materials?page=1&page_size=20")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 6
    assert len(data["items"]) == 6

    # authenticated as user1: should see published + user1 drafts (6 published + 3 drafts = 9)
    r2 = client.get("/materials?page=1&page_size=20", auth=(user1["email"], "password"))
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["total"] == 9
    assert len(d2["items"]) == 9
