import uuid
from functools import lru_cache
from http import HTTPStatus
from logging import getLogger

from fastapi import Depends, HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from werkzeug.security import generate_password_hash

from schemas.base import Page
from schemas.users import UserForCreate
from src.core.config import security_config
from src.db.postgres import get_session
from src.models.db import User, UserRole
from .base import BaseService

logger = getLogger('users_service')


class UsersService(BaseService):

    async def create_user(self, user: UserForCreate) -> User:
        logger.info(f'create_user({user.username=})')
        user_in_db = User(
            username=user.username,
            password_hash=generate_password_hash(user.password, method=security_config.hashing_method.lower(),
                                                 salt_length=security_config.hashing_salt_length),
            full_name=user.full_name,
            email=user.email
        )
        try:
            self.session.add(user_in_db)
            await self.session.commit()
        except IntegrityError as e:
            logger.debug(f'{e=}')
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail='Пользователь с такими данными уже существует.')
        return user_in_db

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        logger.info(f'get_by_id({user_id=})')
        return await self.session.get(User, user_id)

    async def get_by_username(self, username) -> User:
        logger.info(f'get_by_username({username=})')
        result = await self.session.execute(
            select(User).where(User.username == username).options(selectinload(User.roles))
        )
        return result.scalars().one_or_none()

    async def get_roles(self, user_id: uuid.UUID) -> User:
        logger.info(f'')
        result = await self.session.execute(
            select(User).where(User.id == user_id).options(selectinload(User.roles), selectinload(User.history))
        )
        result = result.scalars().one_or_none()
        return result

    async def get_many(self, last_user_id: int = None, limit: int = 10) -> list[User]:
        logger.info('get_all')
        query = select(User).options(selectinload(User.roles)).limit(limit)
        if last_user_id:
            query = query.where(User.id > last_user_id)
        data = await self.session.execute(query)
        return data.scalars().all()

    async def get_users(self) -> Page[User]:
        logger.info('get_roles')
        data = await paginate(self.session, select(User))
        return data

    async def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
        logger.info(f'set_role({user_id=}, {role_id=})')
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.commit()
        return user_role

    async def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        logger.info(f'remove_role({user_id=}, {role_id=})')
        result = await self.session.execute(delete(UserRole).where(
            (UserRole.user_id == user_id) & (UserRole.role_id == role_id)
        ))
        await self.session.commit()
        return bool(result)


@lru_cache()
def get_users_service(
        session: AsyncSession = Depends(get_session),
) -> UsersService:
    return UsersService(session=session)
