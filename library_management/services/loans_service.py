from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from library_management.models.db_models import BookDatabase, LoanDatabase, UserDatabase
from library_management.schemas.loans_schemas import LoanPublic, LoanStatus
from library_management.settings import Settings

settings = Settings()


@dataclass
class LoanService:
    session: AsyncSession

    async def get_book(self, book_isbn):
        return await self.session.scalar(
            select(BookDatabase)
            .options(selectinload(BookDatabase.author))  # carrega o author tambem
            .where(BookDatabase.isbn == book_isbn)
        )

    async def get_all_user_loans(self, user):
        return (
            await self.session.scalars(
                select(LoanDatabase).where(
                    LoanDatabase.user_id == user.id,
                )
            )
        ).all()

    async def create_loan(self, book_isbn: str, user: UserDatabase):
        book = await self.get_book(book_isbn)

        active_loans = sum(
            1
            for loan in await self.get_all_user_loans(user)
            if loan.status == LoanStatus.ACTIVE
        )
        has_already_loan = await self.session.scalar(
            select(LoanDatabase)
            .join(BookDatabase)
            .where(
                BookDatabase.isbn == book_isbn,
                LoanDatabase.user_id == user.id,
                LoanDatabase.status == LoanStatus.ACTIVE,
            )
        )
        if has_already_loan:
            raise HTTPException(
                status_code=409, detail='You already a loan with this Book.'
            )

        if not book:
            raise HTTPException(404, detail='Book not found. Verify the ISBN.')
        if active_loans >= settings.MAX_VALUE_LOANS:
            raise HTTPException(
                status_code=409,
                detail='User has reached the maximum number of active loans.',
            )
        if book.availables <= 0:
            raise HTTPException(status_code=409, detail='Book is not available.')

        book.availables -= 1
        loan = LoanDatabase(
            user_id=user.id,
            book_id=book.id,
            due_date=datetime.now(tz=ZoneInfo('UTC')) + timedelta(days=15),
        )

        self.session.add_all([book, loan])
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        await self.session.refresh(loan)

        return LoanPublic.model_validate(loan)

    async def return_loan(self, loan_id: int, user: UserDatabase):
        loan = await self.session.scalar(
            select(LoanDatabase).where(
                LoanDatabase.id == loan_id, LoanDatabase.user_id == user.id
            )
        )

        if not loan:
            raise HTTPException(status_code=404, detail='Loan not exist.')

        if loan.status == LoanStatus.RETURNED:
            raise HTTPException(status_code=409, detail='Loan is already returned.')

        loan.returned_at = datetime.now(tz=ZoneInfo('UTC'))
        loan.status = LoanStatus.RETURNED

        book = await self.session.scalar(
            select(BookDatabase).where(BookDatabase.id == loan.book_id)
        )
        book.availables += 1

        self.session.add_all([loan, book])
        await self.session.commit()

        return LoanPublic.model_validate(loan)
