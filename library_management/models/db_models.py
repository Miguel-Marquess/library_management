from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

registry_table = registry()


@registry_table.mapped_as_dataclass
class UserDatabase:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, onupdate=func.now(), server_default=func.now()
    )


@registry_table.mapped_as_dataclass
class BookDatabase:
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), init=False)
    author: Mapped['Author'] = relationship(back_populates='books')
    isbn: Mapped[str] = mapped_column(nullable=False, unique=True)
    year: Mapped[int]
    publisher: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    availables: Mapped[int] = mapped_column(nullable=False)


@registry_table.mapped_as_dataclass
class Author:
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    books: Mapped[list['BookDatabase']] = relationship(
        # Author -> N books --> One-to-Many
        init=False,
        lazy='selectin',
        back_populates='author',
    )
