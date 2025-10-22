from .users import router as users_router
from .materials import router as materials_router
from .books import router as books_router
from .articles import router as articles_router
from .videos import router as videos_router
from .authors import router as authors_router

__all__ = [
    "users_router",
    "materials_router",
    "books_router",
    "articles_router",
    "videos_router",
    "authors_router",
]
