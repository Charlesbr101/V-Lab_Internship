from app import schemas
from app.db import crud


def test_create_user_author_book_relation(client, db_session, make_user):
    # create user via API using root credentials
    user = make_user("u@example.com", "password")
    assert user["id"] is not None

    # create author via HTTP route (authenticated as the created user)
    person_payload = {"name": "Jane Doe", "birth_date": "1980-01-01"}
    r = client.post("/authors/persons", json=person_payload, auth=(user["email"], "password"))
    assert r.status_code == 201, r.text
    person = r.json()
    assert person["id"] is not None

    # create book via HTTP route (authenticated)
    book_payload = {
        "title": "Example",
        "description": "desc",
        "status": "published",
        "author_id": person["id"],
        "isbn": "9783161484100",
        "page_count": 123,
    }
    r2 = client.post("/materials/books", json=book_payload, auth=(user["email"], "password"))
    assert r2.status_code == 201, r2.text
    book = r2.json()
    assert book["id"] is not None
    assert book["author_id"] == person["id"]
    # book.user_id is set by the server to the authenticated user
    assert book["user_id"] == user["id"]
