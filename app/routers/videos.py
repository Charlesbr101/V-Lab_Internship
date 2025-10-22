from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.db.crud as crud
import app.schemas as schemas
from app.db.database import SessionLocal
from app.deps import get_current_user

router = APIRouter(prefix="/materials/videos", tags=["materials"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Video])
def read_videos(db: Session = Depends(get_db)):
    return crud.get_videos(db)


@router.post("/", response_model=schemas.Video, status_code=status.HTTP_201_CREATED)
def create_video(video: schemas.VideoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.create_video(db, video)
