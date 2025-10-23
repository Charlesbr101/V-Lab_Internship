from datetime import date
from pydantic import BaseModel, EmailStr, PositiveInt, model_validator

# User Schemas
class UserBase(BaseModel):
	email: EmailStr
	password: str

class UserCreate(UserBase):
	pass

class User(UserBase):
	id: PositiveInt
	class Config:
		orm_mode = True
        
# Material Schemas
class MaterialBase(BaseModel):
	title: str
	description: str
	status: str
	author_id: PositiveInt
	user_id: PositiveInt

	@model_validator(mode="before")
	def validate_status(cls, values):
		status = values.get("status") if isinstance(values, dict) else getattr(values, "status", None)

		if status not in ["rascunho", "publicado", "arquivado"]:
			raise ValueError("Invalid material status")
		return values
    
class Material(MaterialBase):
	id: PositiveInt
	type: str
	class Config:
		orm_mode = True

class BookBase(MaterialBase):
	isbn: str
	page_count: PositiveInt

	@model_validator(mode="before")
	def validate_isbn(cls, values):
		isbn = values.get("isbn") if isinstance(values, dict) else getattr(values, "isbn", None)
		# Check ISBN-13 validity
		if len(isbn) == 13 and isbn.isdigit():
			checksum = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(isbn[:-1]))
			checksum = (10 - (checksum % 10)) % 10
			if checksum == int(isbn[-1]):
				return values
		raise ValueError("Invalid ISBN-13")

class PreBookCreate(BookBase):
	# Optional Title and Page_count fields
	title: str | None = None
	page_count: PositiveInt | None = None

class BookCreate(BookBase):
	pass

class Book(BookBase):
	id: PositiveInt
	class Config:
		orm_mode = True

class ArticleBase(MaterialBase):
	doi: str

class ArticleCreate(ArticleBase):
	pass

class Article(ArticleBase):
	id: PositiveInt
	class Config:
		orm_mode = True

class VideoBase(MaterialBase):
	duration: PositiveInt  # duration in minutes

class VideoCreate(VideoBase):
	pass

class Video(VideoBase):
	id: PositiveInt
	class Config:
		orm_mode = True

# Author Schemas
class AuthorBase(BaseModel):
    name: str
	
class Author(AuthorBase):
	id: PositiveInt
	type: str
	class Config:
		orm_mode = True
	
class PersonAuthorBase(BaseModel):
	name: str
	birth_date: date

class PersonAuthorCreate(PersonAuthorBase):
	pass

class PersonAuthor(PersonAuthorBase):
	id: PositiveInt
	class Config:
		orm_mode = True


class InstitutionAuthorBase(BaseModel):
	name: str
	city: str
class InstitutionAuthorCreate(InstitutionAuthorBase):
	pass

class InstitutionAuthor(InstitutionAuthorBase):
	id: PositiveInt
	class Config:
		orm_mode = True
