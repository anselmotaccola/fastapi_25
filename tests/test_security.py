from jwt import decode

from fast_zero.security import create_access_token


def test_create_access_token(settings):
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded_data = decode(token, settings.SECRET_KEY, settings.ALGORITHM)

    assert decoded_data['test'] == data['test']
    assert 'exp' in decoded_data
