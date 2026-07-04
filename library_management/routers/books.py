from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from library_management.depends.books_dependencies import BookFilter
from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.models.db_models import Author, BookDatabase
from library_management.schemas.books_schemas import Book, BookList, BookPublic

router = APIRouter(tags=['library'], prefix='/books')


@router.post('/', status_code=201, response_model=BookPublic)
async def insert_books(book: Book, session: Session, current_user: Current_user):

    author_orm = await session.scalar(select(Author).where(Author.id == book.author_id))

    if not author_orm:
        raise HTTPException(
            status_code=404, detail=f'Author with id {book.author_id} not exist.'
        )

    db_book = BookDatabase(**book.model_dump(exclude='author_id'), author=author_orm)

    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book


@router.get('/', status_code=200, response_model=BookList)
async def read_books(filter: BookFilter, current_user: Current_user, session: Session):
    query = select(BookDatabase)
    if filter.isbn:
        book = await session.scalar(
            select(BookDatabase).where(BookDatabase.isbn == filter.isbn)
        )

        return {'books': [book]}

    if filter.author_name:
        query = query.join(Author).where(Author.name.contains(filter.author_name))

    map = {
        'title': lambda v: BookDatabase.title.contains(v),
        'author_id': lambda v: BookDatabase.author_id == v,
        'year': lambda v: BookDatabase.year == v,
        'publisher': lambda v: BookDatabase.publisher.contains(v),
    }

    for key, value in filter.model_dump(exclude_none=True).items():
        if key in map:
            query = query.where(map[key](value))

    result = await session.scalars(query.offset(filter.start).limit(filter.ends))

    return {'books': result}
