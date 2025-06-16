from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fast_zero.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class TodoSchema(BaseModel):
    title: str
    description: str | None = None
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class FilterTodo(FilterPage):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    state: TodoState | None = None


class TodoList(BaseModel):
    todos: list[TodoPublic]


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
