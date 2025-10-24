from datetime import date
from typing import Annotated, TypeVar, Generic, Optional, Dict, List
from pydantic import BaseModel, EmailStr, PositiveInt, PastDate, model_validator, Field
from pydantic.generics import GenericModel
import re

#################################
# Generic pagination envelope
T = TypeVar("T")


class Pagination(GenericModel, Generic[T]):
	items: List[T]
	total: int
	page: int
	page_size: int
	links: Dict[str, Optional[str]]

#########################################
# Error schemas used in route responses
class ErrorItem(BaseModel):
	loc: List[str]
	msg: str
	type: str


class ValidationErrorResponse(BaseModel):
	detail: List[ErrorItem]


class SimpleError(BaseModel):
	detail: str

########################################################
# Common responses mapping to reuse in route decorators
HTTP_ERROR_RESPONSES = {
	400: {"model": ValidationErrorResponse, "description": "Bad Request (validation or integrity error)"},
	403: {"model": SimpleError, "description": "Forbidden"},
	404: {"model": SimpleError, "description": "Not Found"},
}

##################
# User Schemas
class UserBase(BaseModel):
    email: EmailStr = Field(description="User email address (used for login)", example="john@example.com")
    password: Annotated[str, Field(min_length=6, description="User password (minimum 6 characters)", example="password")] 

class UserCreate(UserBase):
	pass

class User(UserBase):
	id: PositiveInt = Field(description="Unique user identifier")
	is_root: bool = Field(default=False, description="Whether the user has root/admin privileges")
	class Config:
		orm_mode = True

##################
# Material Schemas
class MaterialBase(BaseModel):
	title: 	Annotated[str, Field(
		min_length=3, max_length=100, 
		description="Title of the material", 
		example="The Great Gatsby"
	)]
	description: Annotated[str, Field(
		max_length=1000, 
		description="A short description of the material.", 
		example="Lore ipsum dolor sit amet"
	)]
	status: Annotated[str, Field(
		description='Status of the material. Valid values: "draft", "published", "filed"',
		examples=["draft", "published", "filed"]
	)]
	author_id: PositiveInt

	@model_validator(mode="before")
	def validate_status(cls, values):
		status = values.get("status") if isinstance(values, dict) else getattr(values, "status", None)

		if status not in ["draft", "published", "filed"]:
			raise ValueError('Invalid material status. Must be one of: "draft", "published", "filed"')
		return values
    
class Material(MaterialBase):
	id: PositiveInt = Field(description="Material unique identifier")
	user_id: PositiveInt = Field(description="ID of user who created the material")
	type: Annotated[str, Field(description="Type of the material", examples=["book", "article", "video"])]
	class Config:
		orm_mode = True


class BookBase(MaterialBase):
	isbn: Annotated[str, Field(description="ISBN of the book", example="9780980200447")]
	page_count: Annotated[PositiveInt, Field(description="Number of pages in the book")]

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

class BookCreate(BookBase):
	# Optional Title and Page_count fields
	title: Optional[Annotated[str, Field(
		min_length=3, max_length=100, 
		description="Title of the material (Can be ommited if ISBN is provided)",
		example="The Great Gatsby"
	)]] = None
	page_count: Optional[Annotated[PositiveInt, Field(
		description="Number of pages in the book (Can be omitted if ISBN is provided)", 
		example=100
	)]] = None

class BookUpdate(BookBase):
	pass

class Book(BookBase):
	id: PositiveInt = Field(description="Book's material unique identifier")
	user_id: PositiveInt = Field(description="ID of the user who added the book")
	class Config:
		orm_mode = True


class ArticleBase(MaterialBase):
	title: Annotated[str, Field(
		min_length=3, max_length=100, 
		description="Title of the article", 
		example="Advances in AI Research"
	)]
	doi: Annotated[str, Field(
		description="Digital Object Identifier of the article", 
		example="10.1000/xyz123"
	)]

	@model_validator(mode="before")
	def validate_doi(cls, values):
		doi = values.get("doi") if isinstance(values, dict) else getattr(values, "doi", None)
		# Basic DOI format validation
		if not re.match(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", doi, re.IGNORECASE):
			raise ValueError("Invalid DOI format. Must follow the format: 10.1234/yyy987")
		return values

class ArticleCreate(ArticleBase):
	pass

class Article(ArticleBase):
	id: PositiveInt = Field(description="Article's material unique identifier")
	user_id: PositiveInt = Field(description="ID of the user who added the article")
	class Config:
		orm_mode = True


class VideoBase(MaterialBase):
	title: Annotated[str, Field(
		min_length=3, max_length=100,
		description="Title of the video",
		example="Lord of The Rings"
	)]
	duration: Annotated[PositiveInt, Field(
		description="Duration of the video in minutes", 
		example=60
	)]

class VideoCreate(VideoBase):
	pass

class Video(VideoBase):
	id: PositiveInt = Field(description="Video's material unique identifier")
	user_id: PositiveInt = Field(description="ID of the user who added the video")
	class Config:
		orm_mode = True

##################
# Author Schemas
class AuthorBase(BaseModel):
	name: Annotated[str, Field(description="Author name", example="Jane Doe")]
	
class Author(AuthorBase):
	id: PositiveInt = Field(description="Author unique identifier")
	type: Annotated[str, Field(description="Type of the author", examples=["person", "institution"])]
	class Config:
		orm_mode = True
	

class AuthorPersonBase(AuthorBase):
	name: Annotated[str, Field(
		min_length=3, max_length=80, 
		description="Name of the person", 
		example="Jane Doe"
	)]
	birth_date: Annotated[PastDate, Field(
		description="Date in the past with YYYY-MM-DD format", 
		example="1980-05-15"
	)]

	# @model_validator(mode="before")
	# def validate_birth_date(cls, values):
	# 	birth_date = values.get("birth_date") if isinstance(values, dict) else getattr(values, "birth_date", None)
	# 	if birth_date and birth_date >= date.today():
	# 		raise ValueError("Invalid birth_date, must be before today")
	# 	return values
	
class AuthorPersonCreate(AuthorPersonBase):
	pass

class AuthorPerson(AuthorPersonBase):
	id: Annotated[PositiveInt, Field(description="Person's author unique identifier")]
	class Config:
		orm_mode = True


class AuthorInstitutionBase(AuthorBase):
	name: Annotated[str, Field(
		min_length=3, max_length=120, 
		description="Name of the institution", 
		example="Global University"
	)]
	city: Annotated[str, Field(
		min_length=2, max_length=80, 
		description="City where the institution is located", 
		example="Duluth"
	)]

class AuthorInstitutionCreate(AuthorInstitutionBase):
	pass

class AuthorInstitution(AuthorInstitutionBase):
	id: Annotated[PositiveInt, Field(description="Institution's author unique identifier")]
	class Config:
		orm_mode = True
