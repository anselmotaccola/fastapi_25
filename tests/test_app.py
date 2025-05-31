from http import HTTPStatus


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


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'email': 'alice@test.com',
                'username': 'alice',
            }
        ]
    }


def test_read_user(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'alice@test.com',
        'username': 'alice',
    }


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


def test_update_user(client):
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


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'bob@test.com',
        'username': 'bob',
    }


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
