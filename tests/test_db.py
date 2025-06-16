from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Seth', email='seth@seth.com', password='seth123'
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'Seth')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'Seth',
        'email': 'seth@seth.com',
        'password': 'seth123',
        'todos': [],
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_create_todo_error(session, user: User):
    todo = Todo(
        title='Test Todo',
        description='This is a test todo item.',
        state='test',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))
