from http import HTTPStatus

import pytest
from sqlalchemy import select

from library_management.models.db_models import BookDatabase, LoanDatabase
from library_management.schemas.loans_schemas import LoanPublic, LoanStatus


@pytest.mark.asyncio
async def test_create_loan(client, user, token, book_db, session):
    response = client.post(
        f'/loans/{book_db.isbn}',
        headers={'Authorization': f'Bearer {token}'},
    )

    loan = await session.scalar(
        select(LoanDatabase)
        .join(BookDatabase)
        .where(
            BookDatabase.isbn == book_db.isbn,
            LoanDatabase.user_id == user.id,
            LoanDatabase.status == LoanStatus.ACTIVE,
        )
    )

    loan_public = LoanPublic.model_validate(loan)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == loan_public.model_dump(mode='json')
    assert book_db.quantity > book_db.availables


def test_create_loan_has_already_loan(client, loan, token, book_db):
    response = client.post(
        f'/loans/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'You already a loan with this Book.'}


def test_create_loan_book_not_exist(client, token):
    response = client.post(
        f'/loans/{1}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found. Verify the ISBN.'}


def test_create_loan_has_max_limit(client, token, book_db, three_loans):
    response = client.post(
        f'/loans/{book_db.isbn}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'User has reached the maximum number of active loans.'
    }


@pytest.mark.asyncio
async def test_create_loan_book_not_availables(client, session, token, book_db):
    book_db.availables = 0
    session.add(book_db)
    await session.commit()

    response = client.post(
        f'/loans/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book is not available.'}
