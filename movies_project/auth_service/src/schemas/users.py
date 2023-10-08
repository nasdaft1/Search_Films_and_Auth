import uuid
from datetime import datetime
from itertools import permutations
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field

# Регулярное выражение для логина:
# - [a-zA-Z0-9_]: соответствует букве (заглавной или строчной), цифре или нижнему подчёркиванию
username_regex = r'^[a-zA-Z0-9_]+$'

# Регулярное выражение для пароля:
# - \d: соответствует цифре
# - [a-zA-Z]: соответствует букве (заглавной или строчной)
# - \W: соответствует не-буквенно-цифровому символу
# password_regex = r'^(?=.*\d)(?=.*[a-zA-Z])(?=.*\W).+$'  # look-behind, is not supported pydantic_core
required_parts = ('[a-zA-Z]', r'\d', r'[\W_]')
password_regex = '^(' + ')|('.join(list('.*'.join(items) + '.*' for items in permutations(required_parts))) + ')$'


class UserForCreate(BaseModel):
    username: Annotated[str, Query(
        description='Логин. От 5 до 20 символов, может содержать только буквы, цифры и нижнее подчёркивание.',
        min_length=5, max_length=20, regex=username_regex
    )]
    password: Annotated[str, Query(
        description='Пароль. От 8 до 50 символов, должен содержать буквы, цифры и символы.',
        min_length=8, max_length=50, pattern=password_regex
    )]
    full_name: Annotated[str, Query(
        description='ФИО. До 50 символов.',
        min_length=1, max_length=50
    )]
    email: Annotated[EmailStr, Query(
        description='Адрес электронной почты.',
        min_length=1, max_length=50
    )]

    def __repr__(self) -> str:
        return f'<UserForCreate(username={self.username}, email={self.email}>'


class UserForUpdate(UserForCreate):
    id: uuid.UUID
    username: Annotated[str, Query(
        description='Логин. От 5 до 20 символов, может содержать только буквы, цифры и нижнее подчёркивание.',
        min_length=5, max_length=20, regex=username_regex
    )]
    password: Annotated[str, Query(
        description='Пароль. Для подтверждения.',
        min_length=8, max_length=50
    )]
    full_name: Annotated[str, Query(
        description='ФИО. До 50 символов.',
        min_length=1, max_length=50
    )]
    email: Annotated[EmailStr, Query(
        description='Адрес электронной почты.',
        min_length=1, max_length=50
    )]

    def __repr__(self) -> str:
        return f'<UserForUpdate(username={self.username}, email={self.email}>'


class UserInDB(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str
    email: str
    created_at: datetime
    is_deleted: bool

    # roles: list[RoleInDB] = Field(default_factory=list)
    # history: list[UserHistory] = Field(default_factory=list)

    class Config:
        from_attributes = True

    def __repr__(self) -> str:
        return f'<UserInDB(id={self.id}, username={self.username}>'


class UserRoleInDB(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID

    class Config:
        from_attributes = True

    def __repr__(self) -> str:
        return f'<UserRoleInDB(user_id={self.user_id}, role_id={self.role_id}>'


class HistoryForCreate(BaseModel):
    user_id: uuid.UUID
    message: str

    def __repr__(self) -> str:
        return f'<HistoryForCreate(user_id={self.user_id}, message={self.message}>'


class HistoryInDB(HistoryForCreate):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

    def __repr__(self) -> str:
        return f'<HistoryInDB(id={self.id}, user_id={self.user_id}, message={self.message}>'


class UserHistory(HistoryInDB):
    user_id: uuid.UUID = Field(exclude=True)

    def __repr__(self) -> str:
        return f'<UserHistory(id={self.id}, message={self.message}>'
