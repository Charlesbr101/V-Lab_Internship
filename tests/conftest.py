"""Pytest fixtures for tests.

This file intentionally requires a MySQL test server and does not provide any
SQLite fallback. Run `make test-mysql` (which starts the test compose) before
running pytest locally, or set `TEST_DATABASE_URL` in the environment.
"""

import os
import time
from pathlib import Path
import sys
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

import app.db.database as db_mod
from app.db.database import Base
from app.db.models import User as UserModel
from app.core.security import pwd_context


def _read_env_test(repo_root: Path) -> dict:
    env = {}
    env_test_path = repo_root / ".env.test"
    if not env_test_path.exists():
        return env
    for line in env_test_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


@pytest.fixture(scope="function")
def db_session():
    """Provide a SQLAlchemy session bound to the MySQL test database.

    This fixture requires the test MySQL server to be available (for example by running
    `make test-mysql` which starts the `docker-compose.test.yml` stack). It will read
    connection settings from `.env.test` (or the environment) and will create the
    test database if necessary. Tables are created before each test and dropped after
    the test to keep runs isolated.
    """
    # Priority: if TEST_DATABASE_URL is already set in environment, use it.
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

    # Otherwise, try to read .env.test to build connection details
    if not TEST_DATABASE_URL:
        repo_root = Path(os.getcwd())
        env = _read_env_test(repo_root)
        MYSQL_HOST = env.get("MYSQL_HOST", os.getenv("MYSQL_HOST", "127.0.0.1"))
        MYSQL_PORT = env.get("MYSQL_TEST_PORT", env.get("MYSQL_PORT", os.getenv("MYSQL_PORT", "3306")))
        MYSQL_ROOT_PASSWORD = env.get("MYSQL_ROOT_PASSWORD", os.getenv("MYSQL_ROOT_PASSWORD", "password"))
        MYSQL_TEST_DB = env.get("MYSQL_TEST_DB", os.getenv("MYSQL_TEST_DB", "digital_library_test"))

        # Wait for MySQL to become available (connect to server without database)
        engine_no_db_url = f"mysql+mysqlconnector://root:{MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/"
        max_retries = 60
        for attempt in range(max_retries):
            try:
                engine_no_db = create_engine(engine_no_db_url)
                with engine_no_db.connect() as conn:
                    conn.execute(text("SELECT 1"))
                break
            except Exception:
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        "Timed out waiting for test MySQL to become available. Ensure `make test-mysql` was run."
                    )
                time.sleep(1)

        # Create the test database if it does not exist
        try:
            engine_no_db = create_engine(engine_no_db_url)
            with engine_no_db.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_TEST_DB}`"))
        except Exception:
            # If creation fails, tests may still work if DB exists; continue and surface
            # errors later during table creation.
            pass

        TEST_DATABASE_URL = (
            f"mysql+mysqlconnector://root:{MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_TEST_DB}"
        )

    if not TEST_DATABASE_URL:
        raise RuntimeError(
            "No TEST_DATABASE_URL was provided and .env.test was not found; tests must run against the test MySQL server."
        )

    # Expose the constructed URL to subprocesses/tests if needed
    os.environ["TEST_DATABASE_URL"] = TEST_DATABASE_URL

    # Create engine and bind it into the app's db module so tests that imported
    # app.db.database earlier will pick up the test engine/sessionmaker.
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    db_mod.engine = engine
    db_mod.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Ensure tables exist for the test run
    Base.metadata.create_all(bind=engine)

    # Seed root user into the test database (if missing). Use env overrides if present.
    root_email = os.getenv("TEST_ROOT_EMAIL", "root@example.com")
    root_password = os.getenv("TEST_ROOT_PASSWORD", "rootpass")
    seed_session = db_mod.SessionLocal()
    try:
        existing = seed_session.query(UserModel).filter(UserModel.email == root_email).first()
        if not existing:
            hashed = pwd_context.hash(root_password)
            u = UserModel(email=root_email, password=hashed, is_root=True)
            seed_session.add(u)
            seed_session.commit()
    finally:
        seed_session.close()

    session = db_mod.SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Tear down tables to keep test runs isolated.
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            pass


@pytest.fixture(scope="session")
def root_credentials():
    """Return (email, password) for the seeded root user."""
    # Allow overriding via environment for CI
    email = os.getenv("TEST_ROOT_EMAIL", "root@example.com")
    password = os.getenv("TEST_ROOT_PASSWORD", "rootpass")
    return (email, password)


# (Root user seeding is performed inside db_session after tables are created.)


@pytest.fixture(scope="function")
def make_user(client, root_credentials):
    """Return a helper to create non-root users via the API using root credentials.

    Usage:
        user = make_user("user@example.com", "password")
    """
    root_auth = root_credentials

    def _make_user(email: str, password: str = "password"):
        payload = {"email": email, "password": password}
        r = client.post("/users", json=payload, auth=root_auth)
        assert r.status_code == 201, r.text
        return r.json()

    return _make_user


@pytest.fixture(scope="function")
def client(db_session):
    """Return a TestClient instance bound to the application configured for tests.

    This fixture ensures app modules are re-imported so the application binds to the
    test database engine created in `db_session`.
    """
    # Reload app modules so they bind to the test DB engine/sessionmaker
    for mod in list(sys.modules.keys()):
        if mod == "app.main" or mod.startswith("app.routers") or mod == "app.deps":
            del sys.modules[mod]

    from app.main import app

    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()