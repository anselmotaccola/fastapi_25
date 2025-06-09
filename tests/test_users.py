from http import HTTPStatus

from fast_zero.schemas import UserPublic
from fast_zero.security import create_access_token


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'password': 'secret',
            'email': 'alice@test.com',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': 'alice@test.com',
        'username': 'alice',
    }


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_get_user_not_found_negativo(client):
    response = client.get(
        '/users/-10',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user_not_found(client):
    response = client.get(
        '/users/100',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'password': 'bob', 'email': 'bob@test.com', 'username': 'bob'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'bob@test.com',
        'username': 'bob',
    }


def test_update_user_not_Auto(client, user):
    data = {'sub': 'test@test'}
    token = create_access_token(data)
    response = client.put(
        '/users/-1',
        headers={'Authorization': f'Bearer {token}'},
        json={'password': 'bob', 'email': 'bob@test.com', 'username': 'bob'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid authentication credentials'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_update_integrity_error(client, user, token):
    client.post(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'fausto@test.com',
            'password': 'secret',
        },
    )
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'fausto@test.com',
            'password': 'teste',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_create_integrity_error_user(client, user):
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@test.com',
            'password': 'secret',
        },
    )
    response = client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@test.com',
            'password': 'teste',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_integrity_error_email(client, user):
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@test.com',
            'password': 'secret',
        },
    )
    response = client.post(
        '/users/',
        json={
            'username': 'fausto1',
            'email': 'fausto@test.com',
            'password': 'teste',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_get_current_user_does_not_exists__ex(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid authentication credentials'}
