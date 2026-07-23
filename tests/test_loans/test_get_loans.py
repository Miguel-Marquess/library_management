from http import HTTPStatus

from library_management.schemas.loans_schemas import LoanPublic


def test_my_loans(three_loans, client, token):
    response = client.get('/loans', headers={'Authorization': f'Bearer {token}'})

    loans = [
        LoanPublic.model_validate(loan).model_dump(mode='json') for loan in three_loans
    ]

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'loans': loans}
