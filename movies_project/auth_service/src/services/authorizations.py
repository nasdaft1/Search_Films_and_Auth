import logging
from functools import lru_cache
from logging import getLogger

import sqlalchemy as sql
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from core.config import security_config
from db.postgres import get_session
from models.db import User, Role
from .base import BaseService

# from db.models import Access
logger = getLogger('users_service')


class Auth(BaseService):



    async def access_user(self, username: str, password: str):
        """
        Проверка есть зарегистрированные user
        если нет его регистрация в DB
        :param username: логин
        :param password: пароль
        :return: код UUID пользователя | None нет доступа
        """
        password_hash = generate_password_hash(
            password, method=security_config.hashing_method.lower(),
            salt_length=security_config.hashing_salt_length),

        statement = (sql.select(User.id, Role.id, Role.name).
                     where(sql.and_(User.username == username,
                                    User.password_hash == password_hash)).limit(1))
        result = (await (self.session.execute(statement))).one_or_none()

        if result is None:
            logging.debug(f'user={username} доступ закрыт')
            return None
        logging.debug(f'user={username} Authorization: Bearer <{result[0]}>')

    async def logout(self):
        """Разлогирование пользователя"""
        pass


def get_auth_service(
        session: AsyncSession = Depends(get_session),
) -> Auth:
    return Auth(session=session)
