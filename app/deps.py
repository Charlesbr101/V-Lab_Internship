from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import User

security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    """Validate basic auth credentials against the users table.

    This performs a simple lookup by email==username and plaintext password comparison.
    Password hashing is recommended for production.
    """
    user = db.query(User).filter(User.email == credentials.username).first()
    if user is None or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """Optional Basic auth: return User if valid Basic auth header present, else None.

    This function intentionally does not raise on invalid or missing credentials so
    it can be used by public GET endpoints that show extra data to authenticated users.
    """
    from fastapi import Request
    import base64

    # request may be passed in by FastAPI
    if not isinstance(request, Request):
        return None

    auth = request.headers.get("authorization")
    if not auth:
        return None

    try:
        scheme, token = auth.split(" ", 1)
        if scheme.lower() != "basic":
            return None
        decoded = base64.b64decode(token).decode()
        username, password = decoded.split(":", 1)
    except Exception:
        return None

    user = db.query(User).filter(User.email == username).first()
    if user is None or user.password != password:
        return None
    return user
