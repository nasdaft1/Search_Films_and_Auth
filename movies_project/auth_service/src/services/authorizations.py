from logging import getLogger
from uuid import UUID

import sqlalchemy as sql
from fastapi import Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash

from core.config import security_config
from db import redis
from db.postgres import get_session
from models.base import UserAccess, Token
from models.db import User, Role
from services.auth import create_all_cookies
from services.users import HistoryForCreate
from services.users import UsersService
from .base import BaseService
from .token import read_token

logger = getLogger('users_service')


class Auth(BaseService):

    async def create_msg(self, data: Token, msg: str):
        if data.user_id:
            await UsersService(self.session).add_history(HistoryForCreate(user_id=UUID(data.user_id), message=msg))

    async def access_user(self, username: str, password: str, response: Response) -> UserAccess:
        """
        Проверка есть зарегистрированные user
        если нет его регистрация в DB
        :param username: логин
        :param password: пароль
        :param response: Response
        :return: model Token = {user_id, roles}
        """
        statement = (sql.select(User.password_hash, User.id).
                     where(User.username == username).limit(1))
        hash_result = (await self.session.execute(statement)).one_or_none()
        if hash_result is None:
            raise HTTPException(status_code=403, detail='В доступе отказано неверный логин')

        password_hash = check_password_hash(pwhash=hash_result[0], password=password)
        user_id = str(hash_result[1])
        if password_hash is False:
            raise HTTPException(status_code=403, detail='В доступе отказано неверный пароль')

        statement = (sql.select(Role.name).
                     where(User.username == username))
        result = (await (self.session.execute(statement))).fetchall()

        roles = [index[0] for index in result]

        if result is None:
            raise HTTPException(status_code=403, detail='В доступе отказано авторизуйтесь')
        create_all_cookies(config=security_config,
                           data=Token(
                               user_id=user_id,
                               roles=roles),
                           response=response)
        return UserAccess(username=username, roles=roles, user_id=user_id)

    async def login(self, data: Token):
        await self.create_msg(data, 'Вы успешно вышли из системы')

    async def logout(self, response: Response, request: Request):
        """Разлогирование пользователя"""
        data = Token
        for index in range(2):
            cookies_name = security_config.token_name[index]
            try:
                token = request.cookies.get(cookies_name)
                if token is None:
                    raise HTTPException(status_code=404,
                                        detail=f'Отсутствует cookies token {cookies_name}')
                data = await read_token(token)
            except HTTPException as error:
                raise HTTPException(status_code=error.status_code,
                                    detail=f'Проверка состояния cookies token {cookies_name}')

            # реализация записи в бд записи что произошел выход из аккаунта
            response.delete_cookie(cookies_name)  # удаление токена
            # внесение токена в black_list
            logger.debug(f'token[{cookies_name}]={str(token)}')

            await redis.set_value(str(token), 1, security_config.token_live[index])
        await self.create_msg(data, 'Вы успешно вышли из системы')
        return 'Вы успешно вышли из системы'


def get_auth_service(
        session: AsyncSession = Depends(get_session),
) -> Auth:
    return Auth(session=session)
