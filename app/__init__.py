"""App package marker.

Creates an explicit package so top-level imports like `import app.main` work
consistently when running scripts from the repository root or via uvicorn.
"""

__all__ = ["main", "models", "schemas", "routers", "db"]
