from http import HTTPStatus

from fast_zero.security import create_access_token


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'


def test_get_token_invalid_credentials_pasword(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrongpassword'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid credentials'}


def test_get_token_invalid_credentials_ex(client):
    data = {'no-username': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_token_invalid_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearertoeken_invalid'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}
