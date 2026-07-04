from typing import Annotated

from fastapi import Query

from library_management.schemas.books_schemas import FilterBook

BookFilter = Annotated[FilterBook, Query()]
