# V-Lab Digital Library Backend

This project is a REST API for managing a digital library, built for the V-Lab selection process. It uses MySQL as the database and Swagger for API documentation.

## Features
- Manage books, authors, and categories
- CRUD operations for library resources
- RESTful endpoints
- Swagger UI for API documentation

## Tech Stack
- Python (FastAPI)
- MySQL
- Swagger (via FastAPI's OpenAPI)

## Setup Instructions
1. Clone the repository
2. Install dependencies (see below)
3. Configure MySQL connection in `.env`
4. Run the API server

## Install Dependencies
```bash
pip install fastapi uvicorn mysql-connector-python python-dotenv
```

## Run the API (development)
Use the Makefile targets which set up the virtualenv and run the app.

```bash
# start MySQL and initialize the DB
make db-up

# start the development server with auto-reload
make run
```

## API Documentation
Once running, access Swagger UI at: `http://localhost:8000/docs`

## Project Structure
- `app/` — application package
	- `app/main.py` — FastAPI app entry point
	- `app/models.py` — SQLAlchemy models
	- `app/schemas.py` — Pydantic schemas
	- `app/db/` — database package (engine, session, migrations)
	- `app/routers/` — route modules
- `initialize_db.py` — development DB initialization and seed
- `docker-compose.yml` — MySQL service for local development
- `Makefile` — convenience tasks (venv, db-up, run, smoke-test)
- `.env` — Environment variables