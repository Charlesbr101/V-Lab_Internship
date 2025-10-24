import pytest

from app import schemas
from app.db import crud


def test_password_hash_and_verify_via_http(client, db_session, make_user):
    # create user via API
    user = make_user("auth@example.com", "password")

    # attempt to create a book via HTTP authenticated as the user; if auth fails,
    # the endpoint will return 401/403. Successful creation implies password verify.
    person_payload = {"name": "Auth Author", "birth_date": "1985-01-01"}
    r_person = client.post("/authors/persons", json=person_payload, auth=(user["email"], "password"))
    assert r_person.status_code == 201, r_person.text
    person = r_person.json()

    book_payload = {
        "title": "Auth Book",
        "description": "d",
        "status": "published",
        "author_id": person["id"],
        "isbn": "9783161484100",
        "page_count": 10,
    }
    r = client.post("/materials/books", json=book_payload, auth=(user["email"], "password"))
    assert r.status_code == 201, r.text


def test_auth_failure_via_http(client, db_session):
    # wrong credentials should fail to authenticate when calling an endpoint
    person_payload = {"name": "Noone Author", "birth_date": "1990-01-01"}
    r = client.post("/authors/persons", json=person_payload, auth=("noone@example.com", "password"))
    assert r.status_code in (401, 403)


def test_optional_auth_returns_none_on_bad(client, db_session):
    # calling an endpoint that allows optional auth with bad credentials should still succeed
    r = client.get("/materials?page=1&page_size=1", auth=("noone", "x"))
    assert r.status_code == 200
