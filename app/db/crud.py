from sqlalchemy.orm import Session
from app.db.models import User, Book, Article, Video, PersonAuthor, InstitutionAuthor, Material
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

def get_materials(db: Session):
    materials = db.query(Material).order_by(Material.id).all()
    return materials

def get_books(db: Session):
    return db.query(Book).all()

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

def get_articles(db: Session):
    return db.query(Article).all()

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

def get_videos(db: Session):
    return db.query(Video).all()

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
