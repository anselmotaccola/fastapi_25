from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterPage = Annotated[FilterPage, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(
    user: UserSchema,
    session: Session,
):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get(
    '/{user_id}/', status_code=HTTPStatus.OK, response_model=UserPublic
)
async def read_user(user_id: int, session: Session):
    user_db = await session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    return user_db


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: Session,
    filter_page: FilterPage,
    current_user=Depends(get_current_user),
):
    users = await session.scalars(
        select(User).limit(filter_page.limit).offset(filter_page.offset)
    )
    return {'users': users}


@router.put(
    '/{user_id}/',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to update this user',
        )
    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists',
            status_code=HTTPStatus.CONFLICT,
        )


@router.delete(
    '/{user_id}/', status_code=HTTPStatus.OK, response_model=Message
)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to update this user',
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted successfully'}
