from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_nova_rota_retorna_html_ola_mundo(client):
    response = client.get('/nova')

    assert response.status_code == HTTPStatus.OK
    assert '<h1> Olá Mundo </h1>' in response.text


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


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={'password': 'bob', 'email': 'bob@test.com', 'username': 'bob'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'bob@test.com',
        'username': 'bob',
    }


def test_update_user_not_found(client):
    response = client.put(
        '/users/100',
        json={'password': 'bob', 'email': 'bob@test.com', 'username': 'bob'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user_not_found_negativo(client):
    response = client.put(
        '/users/-10',
        json={'password': 'bob', 'email': 'bob@test.com', 'username': 'bob'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_not_found(client):
    response = client.delete(
        '/users/100',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_not_found_negativo(client):
    response = client.delete(
        '/users/-10',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_integrity_error(client, user):
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@test.com',
            'password': 'secret',
        },
    )
    response_update = client.put(
        f'/users/{user.id}',
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


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'
