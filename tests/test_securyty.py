from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_create_access_token():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded_data = decode(token, SECRET_KEY, ALGORITHM)

    assert decoded_data['test'] == data['test']
    assert 'exp' in decoded_data
