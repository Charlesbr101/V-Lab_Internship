from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
import app.db.models as models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Library API", description="REST API for managing a digital library.", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import (
    users_router,
    materials_router,
    books_router,
    articles_router,
    videos_router,
    authors_router,
)

app.include_router(users_router)
# Include specific material-type routers before the generic /materials router
app.include_router(books_router)
app.include_router(articles_router)
app.include_router(videos_router)
app.include_router(materials_router)
app.include_router(authors_router)
