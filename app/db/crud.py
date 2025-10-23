from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models import User, Book, Article, Video, AuthorPerson, AuthorInstitution, Material, Author
from app.schemas import UserCreate, BookCreate, ArticleCreate, VideoCreate, AuthorPersonCreate, AuthorInstitutionCreate
from app.core.security import pwd_context

def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_material(db: Session, material_id: int):
    return db.query(Material).filter(Material.id == material_id).first()

def create_user(db: Session, user: UserCreate):
    """Create a new user and store a hashed password."""
    data = user.model_dump()
    # Hash the plaintext password before storing
    if "password" in data and data["password"]:
        data["password"] = pwd_context.hash(data["password"])
    db_user = User(**data)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise

def get_materials(db: Session, user=None, title: str = None, author_name: str = None, description: str = None, page: int = 1, page_size: int = 10):
    """Return materials that are published or belong to the given user.

    Optional filters: title, author_name, description (case-insensitive substring).
    """
    q = db.query(Material)

    # filter by author name across person/institution authors
    if author_name:
        q = q.outerjoin(AuthorPerson, Material.author_id == AuthorPerson.id).outerjoin(
            AuthorInstitution, Material.author_id == AuthorInstitution.id
        ).filter(
            or_(AuthorPerson.name.ilike(f"%{author_name}%"), AuthorInstitution.name.ilike(f"%{author_name}%"))
        )

    if title:
        q = q.filter(Material.title.ilike(f"%{title}%"))

    if description:
        q = q.filter(Material.description.ilike(f"%{description}%"))

    if user is None:
        q = q.filter(Material.status == "published")
    else:
        q = q.filter((Material.status == "published") | (Material.user_id == user.id))

    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(Material.id).limit(page_size).offset(offset).all()
    return items, total


def get_books(db: Session, user=None, title: str = None, author_name: str = None, description: str = None, page: int = 1, page_size: int = 10):
    q = db.query(Book)

    if author_name:
        q = q.outerjoin(AuthorPerson, Book.author_id == AuthorPerson.id).outerjoin(
            AuthorInstitution, Book.author_id == AuthorInstitution.id
        ).filter(
            or_(AuthorPerson.name.ilike(f"%{author_name}%"), AuthorInstitution.name.ilike(f"%{author_name}%"))
        )

    if title:
        q = q.filter(Book.title.ilike(f"%{title}%"))

    if description:
        q = q.filter(Book.description.ilike(f"%{description}%"))

    if user is None:
        q = q.filter(Book.status == "published")
    else:
        q = q.filter((Book.status == "published") | (Book.user_id == user.id))
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(Book.id).limit(page_size).offset(offset).all()
    return items, total

def create_book(db: Session, book: BookCreate, user_id: int):
    db_book = Book(**book.model_dump(), user_id=user_id)
    try:
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except Exception:
        db.rollback()
        raise

def get_articles(db: Session, user=None, title: str = None, author_name: str = None, description: str = None, page: int = 1, page_size: int = 10):
    q = db.query(Article)

    if author_name:
        q = q.outerjoin(AuthorPerson, Article.author_id == AuthorPerson.id).outerjoin(
            AuthorInstitution, Article.author_id == AuthorInstitution.id
        ).filter(
            or_(AuthorPerson.name.ilike(f"%{author_name}%"), AuthorInstitution.name.ilike(f"%{author_name}%"))
        )

    if title:
        q = q.filter(Article.title.ilike(f"%{title}%"))

    if description:
        q = q.filter(Article.description.ilike(f"%{description}%"))

    if user is None:
        q = q.filter(Article.status == "published")
    else:
        q = q.filter((Article.status == "published") | (Article.user_id == user.id))
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(Article.id).limit(page_size).offset(offset).all()
    return items, total

def create_article(db: Session, article: ArticleCreate, user_id: int):
    db_article = Article(**article.model_dump(), user_id=user_id)
    try:
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception:
        db.rollback()
        raise

def get_videos(db: Session, user=None, title: str = None, author_name: str = None, description: str = None, page: int = 1, page_size: int = 10):
    q = db.query(Video)

    if author_name:
        q = q.outerjoin(AuthorPerson, Video.author_id == AuthorPerson.id).outerjoin(
            AuthorInstitution, Video.author_id == AuthorInstitution.id
        ).filter(
            or_(AuthorPerson.name.ilike(f"%{author_name}%"), AuthorInstitution.name.ilike(f"%{author_name}%"))
        )

    if title:
        q = q.filter(Video.title.ilike(f"%{title}%"))

    if description:
        q = q.filter(Video.description.ilike(f"%{description}%"))

    if user is None:
        q = q.filter(Video.status == "published")
    else:
        q = q.filter((Video.status == "published") | (Video.user_id == user.id))

    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(Video.id).limit(page_size).offset(offset).all()
    return items, total

def create_video(db: Session, video: VideoCreate, user_id: int):
    db_video = Video(**video.model_dump(), user_id=user_id)
    try:
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return db_video
    except Exception:
        db.rollback()
        raise

def get_authors(db: Session, page: int = 1, page_size: int = 10):
    q = db.query(Author)
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(Author.id).limit(page_size).offset(offset).all()
    return items, total

def get_person_authors(db: Session, page: int = 1, page_size: int = 10):
    q = db.query(AuthorPerson)
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(AuthorPerson.id).limit(page_size).offset(offset).all()
    return items, total

def create_person_author(db: Session, author: AuthorPersonCreate):
    db_author = AuthorPerson(**author.model_dump())
    try:
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
        return db_author
    except Exception:
        db.rollback()
        raise

def get_institution_authors(db: Session, page: int = 1, page_size: int = 10):
    q = db.query(AuthorInstitution)
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(AuthorInstitution.id).limit(page_size).offset(offset).all()
    return items, total

def create_institution_author(db: Session, author: AuthorInstitutionCreate):
    db_author = AuthorInstitution(**author.model_dump())
    try:
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
        return db_author
    except Exception:
        db.rollback()
        raise


def get_book(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()


def get_article(db: Session, article_id: int):
    return db.query(Article).filter(Article.id == article_id).first()


def update_book(db: Session, book_id: int, data: dict):
    db_book = get_book(db, book_id)
    if db_book is None:
        return None
    for key, value in data.items():
        if hasattr(db_book, key):
            setattr(db_book, key, value)
    try:
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except Exception:
        db.rollback()
        raise


def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if db_book is None:
        return None
    try:
        db.delete(db_book)
        db.commit()
        return db_book
    except Exception:
        db.rollback()
        raise


def get_article(db: Session, article_id: int):
    return db.query(Article).filter(Article.id == article_id).first()


def update_article(db: Session, article_id: int, data: dict):
    db_article = get_article(db, article_id)
    if db_article is None:
        return None
    for key, value in data.items():
        if hasattr(db_article, key):
            setattr(db_article, key, value)
    try:
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception:
        db.rollback()
        raise


def delete_article(db: Session, article_id: int):
    db_article = get_article(db, article_id)
    if db_article is None:
        return None
    try:
        db.delete(db_article)
        db.commit()
        return db_article
    except Exception:
        db.rollback()
        raise


def get_video(db: Session, video_id: int):
    return db.query(Video).filter(Video.id == video_id).first()


def get_author(db: Session, author_id: int):
    return db.query(Author).filter(Author.id == author_id).first()


def get_person_author(db: Session, person_id: int):
    return db.query(AuthorPerson).filter(AuthorPerson.id == person_id).first()


def get_institution_author(db: Session, inst_id: int):
    return db.query(AuthorInstitution).filter(AuthorInstitution.id == inst_id).first()


def update_video(db: Session, video_id: int, data: dict):
    db_video = get_video(db, video_id)
    if db_video is None:
        return None
    for key, value in data.items():
        if hasattr(db_video, key):
            setattr(db_video, key, value)
    try:
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return db_video
    except Exception:
        db.rollback()
        raise


def delete_video(db: Session, video_id: int):
    db_video = get_video(db, video_id)
    if db_video is None:
        return None
    try:
        db.delete(db_video)
        db.commit()
        return db_video
    except Exception:
        db.rollback()
        raise


def update_user(db: Session, user_id: int, data: dict):
    """Update an existing user. If `password` is present it will be hashed."""
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    # handle password hashing if supplied
    if "password" in data and data.get("password"):
        data["password"] = pwd_context.hash(data["password"])
    for key, value in data.items():
        if hasattr(db_user, key) and key != "id":
            setattr(db_user, key, value)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    try:
        db.delete(db_user)
        db.commit()
        return db_user
    except Exception:
        db.rollback()
        raise
