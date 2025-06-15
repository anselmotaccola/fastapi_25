from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import TodoPublic, TodoState
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])


Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
async def create_todo(todo: TodoState, session: Session, user: CurrentUser):
    db_todo = Todo(
        name=todo.name,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo
