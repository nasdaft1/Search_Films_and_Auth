import logging
from logging import getLogger

import sqlalchemy as sql
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from core.config import security_config
from db.postgres import get_session
from models.db import User, Role
from .base import BaseService
from models.base import UserAccess

# from db.models import Access
logger = getLogger('users_service')


class Auth(BaseService):

    async def access_user(self, username: str, password: str) -> UserAccess:
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
        logger.debug('111111111111111111111111111111')
        logger.debug(password, password_hash)
        statement = (sql.select(User.id, Role.id, Role.name).
                     where(sql.and_(User.username == username,
                                    User.password_hash == password_hash)))
        result = (await (self.session.execute(statement))).fetchall()
        roles = []
        for index in result:
            roles.append(index)

        if result is None:
            raise HTTPException(status_code=403, detail="В доступе отказано авторизуйтесь")
        return UserAccess(username=username, roles=roles)

    async def logout(self):
        """Разлогирование пользователя"""
        pass


def get_auth_service(
        session: AsyncSession = Depends(get_session),
) -> Auth:
    return Auth(session=session)
