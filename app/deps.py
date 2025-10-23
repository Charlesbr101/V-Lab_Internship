from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import User

security = HTTPBasic()
# optional security dependency (does not auto-error) so Swagger shows the field but it's optional
security_optional = HTTPBasic(auto_error=False)


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


def get_current_user_optional(
    credentials: Optional[HTTPBasicCredentials] = Depends(security_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional Basic auth: return User when valid credentials are supplied, else None.

    Uses the HTTPBasic security dependency with auto_error=False so OpenAPI/Swagger
    shows the Authorization input but the dependency does not force authentication.
    """
    if credentials is None:
        return None

    user = db.query(User).filter(User.email == credentials.username).first()
    if user is None or user.password != credentials.password:
        return None
    return user
