# V-Lab Digital Library Backend

This project is a REST API for managing a digital library, built for the V-Lab selection process. It uses MySQL as the database and Swagger for API documentation.

This project was made considering a WSL enviroment integrated with windows' desktop docker

## Features
- Manage books, authors, and categories
- CRUD operations for library resources
- RESTful endpoints
- Swagger UI for API documentation

## Tech Stack
- Python (FastAPI)
- MySQL
- Swagger (via FastAPI's OpenAPI)

## WSL + Docker Desktop (Windows)

For developing in WSL (Ubuntu, Debian, etc.) with Docker Desktop for Windows and WSL integration enabled, follow these notes to run the app and tests reliably.

Quick setup (WSL)

1. Ensure WSL2 is installed and your distro is running (Ubuntu recommended).
2. Install Docker Desktop for Windows and enable "Use the WSL 2 based engine" and the WSL integration for your distro in Docker Desktop Settings -> Resources -> WSL Integration.
3. The following setup will be done from WSL's environment

## Project Setup Instructions
1. Clone the repository
2. Install dependencies (see below)
3. Configure MySQL connection in `.env`
4. Run the API server

## Install Dependencies
```bash
# from project root (WSL)
make venv        # creates .venv
source .venv/bin/activate
make install     # installs requirements into .venv
```

## Run the API
Use the Makefile targets which set up the virtualenv and run the app.

```bash
# start MySQL and initialize the DB
make db-up

# start the development server with auto-reload
make run
```

## End the API + database

```bash
# interrupt development server
Ctrl+C

# end database
make db-down
```

## Run Tests

```bash
# run smoke-test for some routes of the API
make smoke-test

# run tests regarding authentication, relations, External API, pagination and data schemas
make tests
```

## API Documentation
Once running, access Swagger UI at: `http://localhost:8000/docs`

## Endpoints (quick reference)
Below is a compact list of the main API endpoints and the primary request/response data shapes. For complete details and examples, open the Swagger UI at `/docs`.

- GET `/` — root health/welcome (no auth)
- GET `/openapi.json` — OpenAPI schema (machine-readable)

- Users (`/users`) -- Only accessible by a authenticated "root" user (created on dataset init)
  - GET `/users` — list users (paginated). Response items: `User` (id, email, is_root).
  - POST `/users` — create user. Request: `UserCreate` (email, password). Response: `User` (201). Auth: authenticated root in current setup.
  - GET `/users/{user_id}`, PUT `/users/{user_id}`, DELETE `/users/{user_id}` — read/update/delete single user (auth required).

- Authors (`/authors`) -- Creation, update and deletion must be done by any authenticated user
  - GET `/authors` — list authors (paginated).
  - Person authors: GET/POST `/authors/persons` — `AuthorPersonCreate` (name, birth_date) → `AuthorPerson`.
  - Institution authors: GET/POST `/authors/institutions` — `AuthorInstitutionCreate` (name, city) → `AuthorInstitution`.

- Materials (polymorphic) (`/materials`) -- Creation, update and deletion must be done by any authenticated user
  - GET `/materials` — list all materials (books, articles, videos) in a `Pagination[Material]` envelope.
  - GET `/materials/{material_id}` — read a material (polymorphic `Material`).

- Books (`/materials/books`) -- Book instances of materials
  - GET `/materials/books` — list books (paginated). Response items: `Book` (id, title, description, status, author_id, user_id, isbn, page_count).
  - POST `/materials/books` — create a book. Request: `BookCreate` (isbn, author_id, status, description; `title` and `page_count` are optional). If `title`/`page_count` omitted and `isbn` provided, the server attempts OpenLibrary enrichment. Response: `Book` (201) or 400 on validation/integrity errors. Auth required.
  - GET/PUT/DELETE `/materials/books/{book_id}` — read/update/delete a book (update/delete require owner auth).

- Articles (`/materials/articles`) -- Articles instances of materials
  - GET `/materials/articles` — list articles. POST `/materials/articles` — create with `ArticleCreate` (title, description, status, author_id, doi). DOI format validated.
  - GET/PUT/DELETE `/materials/articles/{article_id}` — read/update/delete (owner checks apply).

- Videos (`/materials/videos`) -- Videos instances of materials
  - GET `/materials/videos` — list videos. POST `/materials/videos` — create with `VideoCreate` (title, description, status, author_id, duration).
  - GET/PUT/DELETE `/materials/videos/{video_id}` — read/update/delete (owner checks apply).

Notes:
- Auth: HTTP Basic (username = email, password). Endpoints that create/modify resources require auth via the `get_current_user` dependency. Some read endpoints accept optional auth (`get_current_user_optional`).
- Pagination: list endpoints return `Pagination[T]` with fields: `items`, `total`, `page`, `page_size`, and `links` (first/prev/next/last).
- Error handling: validation and integrity errors are returned as structured 400 responses; 403/404 return a simple error with `detail`.

## Project Structure

- `app/` — application package
  - `app/main.py` — FastAPI app entry point and router wiring
  - `app/db/` — database helpers (engine, session factory), models and DB init scripts
  - `app/routers/` — route modules (users, authors, materials, books, articles, videos)
  - `app/schemas.py` — Pydantic schemas used for request/response validation
  - `app/core/` — configuration and security (dotenv loader, password hashing)

- `tests/` — pytest test suite (unit + integration). Contains `conftest.py`, route tests and OpenLibrary mocks.

- `docker-compose.yml` — compose stack for local development (MySQL dev instance).
- `docker-compose.test.yml` — test-only compose stack used by the test runner (isolated MySQL test instance).
- `.env` — environment variables for development (database host/port, root password).
- `.env.test` — test-specific environment overrides used by the test compose (separate DB name and host port).

- `Makefile` — task shortcuts (create virtualenv, install, start/stop DB, run server, run tests).
- `requirements.txt` — pinned Python dependencies for the project.
- `initialize_db.py` — helper to wait for MySQL and seed initial dev data (used by `make db-up`).
- `smoke_test.py` — small script to exercise a few endpoints (used for basic smoke testing).

This list includes the files and folders the test-suite and Makefile targets rely on (for example, `docker-compose.test.yml` and `.env.test` are used when running `make tests`).