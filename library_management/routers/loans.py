from fastapi import APIRouter

from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.schemas.loans_schemas import LoanList, LoanPublic
from library_management.services.loans_service import LoanService

router = APIRouter(tags=['Loans'], prefix='/loans')


@router.post('/{book_isbn}', status_code=201, response_model=LoanPublic)
async def make_loan(book_isbn: str, user: Current_user, session: Session):
    return await LoanService(session).create_loan(book_isbn=book_isbn, user=user)


@router.patch('/{loan_id}/return', status_code=200, response_model=LoanPublic)
async def devolution(loan_id: int, user: Current_user, session: Session):
    return await LoanService(session).return_loan(loan_id, user)


@router.get('/', status_code=200, response_model=LoanList)
async def my_loans(user: Current_user, session: Session):
    return {'loans': await LoanService(session).get_all_user_loans(user)}
