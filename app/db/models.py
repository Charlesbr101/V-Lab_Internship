from app.db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    # flag to indicate a root/admin user with special privileges
    is_root = Column(Boolean, nullable=False, default=False)
    materials = relationship("Material", back_populates="user")

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(String(9), nullable=False)  # draft, published, filed
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False) # discriminator column for polymorphic identity
    user = relationship("User", back_populates="materials")
    author = relationship("Author", back_populates="materials")

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "material",
        "with_polymorphic": "*",
    }

class Book(Material):
    __tablename__ = "books"
    id = Column(Integer, ForeignKey("materials.id"), primary_key=True, index=True)
    isbn = Column(String(13), unique=True, index=True, nullable=False)
    page_count = Column(Integer, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "book",
    }

class Article(Material):
    __tablename__ = "articles"
    id = Column(Integer, ForeignKey("materials.id"), primary_key=True, index=True)
    doi = Column(String(255), unique=True, index=True, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "article",
    }

class Video(Material):
    __tablename__ = "videos"
    id = Column(Integer, ForeignKey("materials.id"), primary_key=True, index=True)
    duration = Column(Integer, nullable=False)  # duration in minutes

    __mapper_args__ = {
        "polymorphic_identity": "video",
    }

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    # discriminator for joined inheritance
    type = Column(String(50), nullable=False)
    materials = relationship("Material", back_populates="author")

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "author",
        "with_polymorphic": "*",
    }

class AuthorPerson(Author):
    __tablename__ = "person_authors"
    id = Column(Integer, ForeignKey("authors.id"), primary_key=True, index=True)
    name = Column(String(80), nullable=False)
    birth_date = Column(Date, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "person",
    }

class AuthorInstitution(Author):
    __tablename__ = "institution_authors"
    id = Column(Integer, ForeignKey("authors.id"), primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    city = Column(String(80), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "institution",
    }
