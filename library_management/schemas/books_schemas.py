from pydantic import BaseModel, ConfigDict

from library_management.schemas.core_schemas import FilterPage


class Book(BaseModel):
    title: str
    author_id: int
    isbn: str
    year: int
    publisher: str
    quantity: int
    availables: int


class BookPublic(Book):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookList(BaseModel):
    books: list[BookPublic]


class AuthorSchema(BaseModel):
    name: str


class AuthorPublic(AuthorSchema):
    id: int


class FilterBook(FilterPage):
    title: str | None = None
    author_id: int | None = None
    author_name: str | None = None
    year: int | None = None
    publisher: str | None = None
    isbn: str | None = None
