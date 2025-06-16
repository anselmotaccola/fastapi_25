from http import HTTPStatus

import factory.fuzzy
import pytest

from fast_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Todo',
                'description': 'This is a test todo item.',
                'state': 'draft',
            },
        )

    # assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'This is a test todo item.',
        'state': 'draft',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(expected_todos, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2(
    session, user, client, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        f'/todos/?offset=0&limit={expected_todos}',
        headers={'Authorization': f'Bearer {token}'},
        params={'limit': 2, 'offset': 0},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_title_shoul_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, title='Test Title'
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?title=Test Title',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_description_shoul_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, description='Test Description'
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?description=Test Descri',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_state_shoul_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, state=TodoState.trash
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?state=trash',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_delete_todo_error(client, token):
    response = client.delete(
        '/todos/9999', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


@pytest.mark.asyncio
async def test_delete_other_user_todo(session, client, token, other_user):
    todo_other_user = TodoFactory(user_id=other_user.id)
    session.add(todo_other_user)
    await session.commit()

    response = client.delete(
        f'/todos/{todo_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/9999',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Updated Title'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


@pytest.mark.asyncio
async def test_list_todos_should_return_all_expected_todos(
    session, user, client, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json()['todos'] == [
        {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'state': todo.state,
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
        }
    ]
