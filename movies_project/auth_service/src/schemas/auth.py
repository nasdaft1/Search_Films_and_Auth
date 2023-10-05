from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class UserPassAUTH(BaseModel):
    username: Annotated[str, Query(
        description='Логин',
        min_length=5, max_length=20
    )]
    password: Annotated[str, Query(
        description='Пароль',
        min_length=8, max_length=50
    )]
