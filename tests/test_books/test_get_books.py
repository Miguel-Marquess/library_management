from http import HTTPStatus

from library_management.schemas.books_schemas import BookPublic


def get_list_books(*book_db):
    return {'books': [BookPublic.model_validate(book).model_dump() for book in book_db]}


def test_get_book_by_isbn(client, book_db, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'isbn': book_db.isbn},
    )

    assert response.json() == get_list_books(book_db)


def test_invalid_isbn(client, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'isbn': 'invalid'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'ISBN is not valid.'}


def test_get_book_by_author_name(client, book_db, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'author_name': book_db.author.name},
    )

    assert response.json() == get_list_books(book_db)


def test_get_book_by_title(client, book_db, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': book_db.title[:4]},
    )

    assert response.json() == get_list_books(book_db)


def test_get_5_books_by_author_id(client, token, author, many_dicts_books):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'author_id': author.id},
    )

    assert response.json() == {'books': many_dicts_books}

def test_get_books_whos_contains_a(client, token, many_dicts_books):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': 'a'},
    )
    books = [book for book in many_dicts_books if 'a' in book['title']]
             
    assert response.json() == {'books': books}

def test_get_5_books(client, token, many_dicts_books):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'books': many_dicts_books}
