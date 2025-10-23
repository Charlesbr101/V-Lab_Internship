import time
import os
import sys
from datetime import date
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.db.database import engine, SessionLocal
from app.db import models
from app import schemas
from app.schemas import (
    UserCreate,
    AuthorPersonCreate,
    AuthorInstitutionCreate,
    BookCreate,
    ArticleCreate,
    VideoCreate,
)
from pydantic import ValidationError

# Wait for MySQL to become available
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
RETRY_SECONDS = 2
MAX_RETRIES = 30

def wait_for_mysql(host: str, port: int, retry_seconds: int = 2, max_retries: int = 30):
    print(f"Waiting for MySQL at {host}:{port}...")
    for i in range(max_retries):
        try:
            # simple connection check
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("MySQL is available.")
            return True
        except OperationalError:
            print(f"MySQL not ready, retrying in {retry_seconds}s... ({i+1}/{max_retries})")
            time.sleep(retry_seconds)
    print("Failed to connect to MySQL after retries.")
    return False


def _seed(db):
    # Users
    if not db.query(models.User).first():
        try:
            u1 = UserCreate.model_validate({"email": "alice@example.com", "password": "password"})
            u2 = UserCreate.model_validate({"email": "bob@example.com", "password": "password"})
        except ValidationError as ve:
            print("User seed validation failed:", ve)
            raise
        alice = models.User(**u1.model_dump())
        bob = models.User(**u2.model_dump())
        db.add_all([alice, bob])
        db.commit()
        print("Added example users: alice, bob")

    # Authors
    if not db.query(models.AuthorPerson).first() and not db.query(models.AuthorInstitution).first():
        try:
            person_s = AuthorPersonCreate.model_validate({"name": "John Doe", "birth_date": '1970-01-01'})
            inst_s = AuthorInstitutionCreate.model_validate({"name": "Acme Research", "city": "Lisbon"})
        except ValidationError as ve:
            print("Author seed validation failed:", ve)
            raise
        person = models.AuthorPerson(**person_s.model_dump())
        institution = models.AuthorInstitution(**inst_s.model_dump())
        db.add_all([person, institution])
        db.commit()
        print("Added example authors: person and institution")

    # Materials (books, articles, videos)
    if not db.query(models.Book).first():
        user = db.query(models.User).first()
        person_author = db.query(models.AuthorPerson).first()
        institution_author = db.query(models.AuthorInstitution).first()

        try:
            book_s = BookCreate.model_validate(
                {
                    "title": "Example Book",
                    "description": "An example book created during seeding.",
                    "status": "published",
                    "author_id": person_author.id if person_author else None,
                    "isbn": "9783161484100",
                    "page_count": 250,
                }
            )

            article_s = ArticleCreate.model_validate(
                {
                    "title": "Example Article",
                    "description": "An example article created during seeding.",
                    "status": "draft",
                    "author_id": institution_author.id if institution_author else None,
                    "doi": "10.1000/exampledoi",
                }
            )

            video_s = VideoCreate.model_validate(
                {
                    "title": "Example Video",
                    "description": "An example video created during seeding.",
                    "status": "published",
                    "author_id": person_author.id if person_author else None,
                    "duration": 10,
                }
            )
        except ValidationError as ve:
            print("Material seed validation failed:", ve)
            raise

        book = models.Book(**book_s.model_dump(), user_id=user.id if user else None)
        article = models.Article(**article_s.model_dump(), user_id=user.id if user else None)
        video = models.Video(**video_s.model_dump(), user_id=user.id if user else None)

        db.add_all([book, article, video])
        db.commit()
        print("Added example materials: book, article, video")


def main():
    # Wait for MySQL to become available
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    if not wait_for_mysql(MYSQL_HOST, MYSQL_PORT, RETRY_SECONDS, MAX_RETRIES):
        sys.exit(1)

    # Create tables
    print("Creating database tables (if not exists)...")
    models.Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")

    # Seed example data (idempotent)
    print("Seeding example data (if absent)...")

    with SessionLocal() as db:
        try:
            _seed(db)
        except ProgrammingError as e:
            # Possible schema mismatch (existing table without expected columns).
            print("ProgrammingError during seeding:", e)
            print("Attempting to drop and recreate all tables, then retry seeding using a fresh session...")
            try:
                # close the current session before messing with schema
                try:
                    db.close()
                except Exception:
                    pass
                models.Base.metadata.drop_all(bind=engine)
                models.Base.metadata.create_all(bind=engine)
                print("Recreated tables successfully. Retrying seed with a new session...")
                with SessionLocal() as db2:
                    _seed(db2)
            except Exception as ex:
                print("Failed to recreate tables:", ex)
                sys.exit(1)

    print("Seeding complete.")


if __name__ == "__main__":
    main()