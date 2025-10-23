from sqlalchemy.orm import Session
from app.db.models import User, Book, Article, Video, PersonAuthor, InstitutionAuthor, Material, Author
from app.schemas import UserCreate, BookCreate, ArticleCreate, VideoCreate, PersonAuthorCreate, InstitutionAuthorCreate

def get_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.model_dump())
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise

def get_materials(db: Session, user=None):
    """Return materials that are published or belong to the given user.

    If user is None, only published materials are returned.
    """
    q = db.query(Material)
    if user is None:
        q = q.filter(Material.status == "publicado")
    else:
        q = q.filter((Material.status == "publicado") | (Material.user_id == user.id))
    return q.order_by(Material.id).all()


def get_books(db: Session, user=None):
    q = db.query(Book)
    if user is None:
        q = q.filter(Book.status == "publicado")
    else:
        q = q.filter((Book.status == "publicado") | (Book.user_id == user.id))
    return q.all()

def create_book(db: Session, book: BookCreate):
    db_book = Book(**book.model_dump())
    try:
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except Exception:
        db.rollback()
        raise

def get_articles(db: Session, user=None):
    q = db.query(Article)
    if user is None:
        q = q.filter(Article.status == "publicado")
    else:
        q = q.filter((Article.status == "publicado") | (Article.user_id == user.id))
    return q.all()

def create_article(db: Session, article: ArticleCreate):
    db_article = Article(**article.model_dump())
    try:
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception:
        db.rollback()
        raise

def get_videos(db: Session, user=None):
    q = db.query(Video)
    if user is None:
        q = q.filter(Video.status == "publicado")
    else:
        q = q.filter((Video.status == "publicado") | (Video.user_id == user.id))
    return q.all()

def create_video(db: Session, video: VideoCreate):
    db_video = Video(**video.model_dump())
    try:
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return db_video
    except Exception:
        db.rollback()
        raise

def get_authors(db: Session):
    authors = db.query(Author).all()
    return authors

def get_person_authors(db: Session):
    return db.query(PersonAuthor).all()

def create_person_author(db: Session, author: PersonAuthorCreate):
    db_author = PersonAuthor(**author.model_dump())
    try:
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
        return db_author
    except Exception:
        db.rollback()
        raise

def get_institution_authors(db: Session):
    return db.query(InstitutionAuthor).all()

def create_institution_author(db: Session, author: InstitutionAuthorCreate):
    db_author = InstitutionAuthor(**author.model_dump())
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
