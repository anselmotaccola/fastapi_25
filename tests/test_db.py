from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(username='Seth', email='seth@seth.com', password='seth123')
    session.add(user)
    session.commit()
    session.scalar(select(User).where(User.email == 'seth@seth.com'))

    assert user.username == 'Seth'
    assert user.id == 1
    assert user.email == 'seth@seth.com'
    assert user.password == 'seth123'
