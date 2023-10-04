import uuid
from functools import lru_cache
from http import HTTPStatus
from logging import getLogger

from fastapi import Depends, HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from werkzeug.security import generate_password_hash, check_password_hash

from schemas.base import Page
from schemas.users import UserForCreate, HistoryForCreate, UserForUpdate
from src.core.config import security_config
from src.db.postgres import get_session
from src.models.db import User, Role, History
from .base import BaseService

logger = getLogger('users_service')


class UsersService(BaseService):

    async def create_user(self, user: UserForCreate) -> User:
        logger.info(f'create_user({user=})')
        user_in_db = User(
            username=user.username,
            password_hash=generate_password_hash(user.password, method=security_config.hashing_method.lower(),
                                                 salt_length=security_config.hashing_salt_length),
            full_name=user.full_name,
            email=user.email
        )
        try:
            self.session.add(user_in_db)
            await self.session.flush()
            await self.session.commit()
        except IntegrityError as e:
            logger.debug(f'{e=}')
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail='Пользователь с такими данными уже существует.')
        return user_in_db

    async def get_by_id(self, user_id: uuid.UUID, with_roles: bool = False,
                        with_history: bool = False, with_exception: bool = True) -> User:
        logger.info(f'get_by_id({user_id=})')
        query = select(User).where(User.id == user_id)
        options = []
        if with_roles:
            options.append(selectinload(User.roles))
        if with_history:
            options.append(selectinload(User.history))
        if options:
            query = query.options(*options)
        user = await self.session.execute(query)
        user = user.scalars().one_or_none()
        if not user and with_exception:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Пользователь не найден.')
        return user

    async def get_by_username(self, username) -> User:
        logger.info(f'get_by_username({username=})')
        result = await self.session.execute(
            select(User).where(User.username == username).options(selectinload(User.roles))
        )
        return result.scalars().one_or_none()

    async def update_user(self, user: UserForUpdate) -> str:
        logger.info(f'update_user({user=})')
        user_in_db = await self.get_by_id(user_id=user.id, with_exception=False)
        if not user_in_db or not check_password_hash(pwhash=user_in_db.password_hash, password=user.password):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Неправильный логин/id или пароль')
        user_in_db.username = user.username
        user_in_db.full_name = user.full_name
        user_in_db.email = user.email
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.debug(f'{e=}')
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail='Пользователь с такими данными уже существует.')
        return 'OK'

    async def get_roles(self, user_id: uuid.UUID) -> list[Role]:
        logger.info(f'get_roles({user_id=})')
        user = await self.get_by_id(user_id=user_id, with_roles=True)
        return user.roles

    async def get_history(self, user_id: uuid.UUID) -> list[History]:
        logger.info(f'get_history({user_id=})')
        user = await self.get_by_id(user_id=user_id, with_history=True)
        return user.history

    async def add_history(self, history: HistoryForCreate) -> History:
        logger.info(f'add_history({history=})')
        history_in_db = History(user_id=history.user_id, message=history.message)
        try:
            self.session.add(history_in_db)
            await self.session.flush()
            await self.session.commit()
        except IntegrityError as e:
            logger.debug(f'{e=}')
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Пользователь не найден.')
        return history_in_db

    async def get_users(self) -> Page[User]:
        logger.info('get_roles')
        data = await paginate(self.session, select(User))
        return data

    async def add_role(self, user_id: uuid.UUID, role: Role) -> str:
        logger.info(f'set_role({user_id=}, {role.id=})')
        user = await self.get_by_id(user_id=user_id, with_roles=True)
        if role in user.roles:
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail='У пользователя уже есть данная роль.')
        user.roles.append(role)
        await self.session.commit()
        return 'OK'

    async def remove_role(self, user_id: uuid.UUID, role: Role) -> None:
        logger.info(f'remove_role({user_id=}, {role.id=})')
        user = await self.get_by_id(user_id=user_id, with_roles=True)
        if role not in user.roles:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Роль пользователю назначена не была.')
        user.roles.remove(role)
        await self.session.commit()


@lru_cache()
def get_users_service(
        session: AsyncSession = Depends(get_session),
) -> UsersService:
    return UsersService(session=session)
