from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user

router = APIRouter(prefix="/materials", tags=["materials"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Material])
def read_materials(db: Session = Depends(get_db)):
    return crud.get_materials(db)
