import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, EmailStr
from itertools import permutations

from schemas.roles import RoleInDB

# Регулярное выражение для логина:
# - [a-zA-Z0-9_]: соответствует букве (заглавной или строчной), цифре или нижнему подчёркиванию
username_regex = r'^[a-zA-Z0-9_]+$'

# Регулярное выражение для пароля:
# - \d: соответствует цифре
# - [a-zA-Z]: соответствует букве (заглавной или строчной)
# - \W: соответствует не-буквенно-цифровому символу
# password_regex = r'^(?=.*\d)(?=.*[a-zA-Z])(?=.*\W).+$'  # look-behind, is not supported pydantic_core
required_parts = ('[a-zA-Z]', r'\d.', r'[\W_]')
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
    email: EmailStr

    def __repr__(self) -> str:
        return f'<UserForCreate(username={self.username}, email={self.email}>'


class UserHistory(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

    def __repr__(self) -> str:
        return f'<User(id={self.id}, username={self.message}>'


class UserInDB(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str
    email: str
    created_at: datetime
    is_deleted: bool

    roles: list[RoleInDB]
    history: list[UserHistory]

    class Config:
        orm_mode = True
        from_attributes = True

    def __repr__(self) -> str:
        return f'<User(id={self.id}, username={self.username}>'

