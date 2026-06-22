from http import HTTPStatus

def test_should_return_welcome(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Welcome to my Library Management!'}
