from http import HTTPStatus


def test_delete_user(client, token):
    response = client.delete('/users/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User was deleted.'}
