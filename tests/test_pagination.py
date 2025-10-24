from app import schemas
from app.db import crud


def make_isbn13(n: int) -> str:
    """Generate a valid ISBN-13 from an integer seed.

    This builds a 12-digit base by adding n to a fixed prefix and computes
    the ISBN-13 check digit.
    """
    base = str(978000000000 + n)
    base = base[-12:]
    checksum = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
    check = (10 - (checksum % 10)) % 10
    return base + str(check)


def test_books_pagination(client, db_session, make_user):
    # create user via API
    user = make_user("pager@example.com", "password")

    # create author via HTTP
    person_payload = {"name": "Pag Author", "birth_date": "1970-01-01"}
    r_person = client.post("/authors/persons", json=person_payload, auth=(user["email"], "password"))
    assert r_person.status_code == 201, r_person.text
    person = r_person.json()

    # create 15 published books via HTTP
    for i in range(15):
        isbn = make_isbn13(i + 1)
        if len(isbn) != 13:
            isbn = "9783161484100"
        book_payload = {
            "title": f"Book {i}",
            "description": "desc",
            "status": "published",
            "author_id": person["id"],
            "isbn": isbn,
            "page_count": 100 + i,
        }
        r = client.post("/materials/books", json=book_payload, auth=(user["email"], "password"))
        assert r.status_code == 201, r.text

    # page 1: 10 items (via HTTP)
    r1 = client.get("/materials/books?page=1&page_size=10")
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["total"] == 15
    assert len(d1["items"]) == 10

    # page 2: remaining 5 items
    r2 = client.get("/materials/books?page=2&page_size=10")
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["total"] == 15
    assert len(d2["items"]) == 5


def test_materials_visibility_and_pagination(client, db_session, make_user):
    # create users via API
    user1 = make_user("u1@example.com", "password")
    user2 = make_user("u2@example.com", "password")

    # create author via HTTP as user1
    person_payload = {"name": "Vis Author", "birth_date": "1975-01-01"}
    r_person = client.post("/authors/persons", json=person_payload, auth=(user1["email"], "password"))
    assert r_person.status_code == 201, r_person.text
    person = r_person.json()

    # user1 creates 3 drafts and 2 published via HTTP
    for i in range(3):
        isbn = make_isbn13(100 + i)
        if len(isbn) != 13:
            isbn = "9783161484100"
        book_payload = {
            "title": f"U1 Draft {i}",
            "description": "d",
            "status": "draft",
            "author_id": person["id"],
            "isbn": isbn,
            "page_count": 10,
        }
        r = client.post("/materials/books", json=book_payload, auth=(user1["email"], "password"))
        assert r.status_code == 201, r.text

    for i in range(2):
        isbn = make_isbn13(200 + i)
        if len(isbn) != 13:
            isbn = "9783161484100"
        book_payload = {
            "title": f"U1 Pub {i}",
            "description": "d",
            "status": "published",
            "author_id": person["id"],
            "isbn": isbn,
            "page_count": 10,
        }
        r = client.post("/materials/books", json=book_payload, auth=(user1["email"], "password"))
        assert r.status_code == 201, r.text

    # user2 creates 4 published via HTTP
    for i in range(4):
        isbn = make_isbn13(300 + i)
        if len(isbn) != 13:
            isbn = "9783161484100"
        book_payload = {
            "title": f"U2 Pub {i}",
            "description": "d",
            "status": "published",
            "author_id": person["id"],
            "isbn": isbn,
            "page_count": 10,
        }
        r = client.post("/materials/books", json=book_payload, auth=(user2["email"], "password"))
        assert r.status_code == 201, r.text

    # anonymous: only published materials should be visible (2 from user1 + 4 from user2 = 6)
    r = client.get("/materials?page=1&page_size=20")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 6
    assert len(data["items"]) == 6

    # authenticated as user1: should see published + user1 drafts (6 + 3 = 9)
    r2 = client.get("/materials?page=1&page_size=20", auth=(user1["email"], "password"))
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["total"] == 9
    assert len(d2["items"]) == 9
