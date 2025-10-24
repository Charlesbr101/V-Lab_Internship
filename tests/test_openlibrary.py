from app import schemas
import requests


def _make_resp(status_code: int, data: dict):
    class R:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data

        def json(self):
            return self._data

    return R(status_code, data)


def test_openlibrary_enrichment_success(monkeypatch, client, db_session, make_user):
    isbn = "9783161484100"

    # Mock successful OpenLibrary response with title and number_of_pages
    data = {f"ISBN:{isbn}": {"title": "Enriched Title", "number_of_pages": 321}}

    def fake_get(url, timeout=5):
        return _make_resp(200, data)

    monkeypatch.setattr(requests, "get", fake_get)

    # create a user and an author
    user = make_user("ol_user@example.com", "password")
    person_payload = {"name": "OL Author", "birth_date": "1970-01-01"}
    r_person = client.post("/authors/persons", json=person_payload, auth=(user["email"], "password"))
    assert r_person.status_code == 201
    person = r_person.json()

    # Create book with only ISBN (no title/page_count) -> should be enriched
    book_payload = {"isbn": isbn, "author_id": person["id"], "status": "published", "description": "x"}
    r = client.post("/materials/books", json=book_payload, auth=(user["email"], "password"))
    assert r.status_code == 201, r.text
    b = r.json()
    assert b["title"] == "Enriched Title"
    assert b["page_count"] == 321


def test_openlibrary_enrichment_no_data_or_error(monkeypatch, client, db_session, make_user):
    # use a valid ISBN (same valid ISBN used in the success case) so model validation
    # doesn't fail with 422 and we can test enrichment behavior
    isbn = "9783161484100"

    # Case A: API returns 200 but no key present
    def fake_get_empty(url, timeout=5):
        return _make_resp(200, {})

    monkeypatch.setattr(requests, "get", fake_get_empty)

    user = make_user("ol_user2@example.com", "password")
    person_payload = {"name": "OL Author 2", "birth_date": "1970-01-01"}
    r_person = client.post("/authors/persons", json=person_payload, auth=(user["email"], "password"))
    assert r_person.status_code == 201
    person = r_person.json()

    book_payload = {"isbn": isbn, "author_id": person["id"], "status": "published", "description": "x"}
    r = client.post("/materials/books", json=book_payload, auth=(user["email"], "password"))
    # enrichment provided nothing; creation should fail because page_count/title remained missing
    assert r.status_code == 400

    # Case B: network error -> enrichment returns None -> same behavior
    def fake_get_err(url, timeout=5):
        raise requests.exceptions.RequestException("network")

    monkeypatch.setattr(requests, "get", fake_get_err)

    # use a valid ISBN here as well so the request reaches the enrichment logic
    book_payload2 = {"isbn": "9783161484100", "author_id": person["id"], "status": "published", "description": "x"}
    r2 = client.post("/materials/books", json=book_payload2, auth=(user["email"], "password"))
    assert r2.status_code == 400
