import uuid
from http import HTTPStatus
from logging import getLogger

from fastapi import Depends, HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.base import Page
from src.db.postgres import get_session
from src.models.db import Role
from .base import BaseService

logger = getLogger('roles_service')


class RolesService(BaseService):

    async def create_role(self, name: str, service_name: str, description: str) -> Role:
        logger.info(f'create_role({name=}, {service_name=}, {description=})')
        role = Role(name=name, service_name=service_name, description=description)
        try:
            self.session.add(role)
            await self.session.commit()
        except IntegrityError as e:
            logger.debug(f'{e=}')
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Роль с такими данными уже существует.')
        return role

    async def get_by_id(self, role_id: uuid.UUID) -> Role:
        logger.info(f'get_by_id({role_id=})')
        role = await self.session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Роль не найдена.')
        return role

    async def get_by_name(self, name: str) -> Role:
        logger.info(f'get_by_name({name=})')
        result = await self.session.execute(select(Role).where(Role.name == name))
        found = result.scalars().first()
        return found

    async def get_roles(self) -> Page[Role]:
        logger.info('get_roles')
        data = await paginate(self.session, select(Role))
        return data

    async def update_role(self, role_id: uuid.UUID, name: str, service_name: str, description: str) -> str:
        logger.info(f'update_role({role_id=}, {name=}, {service_name=}, {description=})')
        stmt = update(Role).where(Role.id == role_id).values(
            name=name,
            service_name=service_name,
            description=description
        )
        result = await self.session.execute(stmt)
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.debug(f'{e=}')
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Роль с такими данными уже существует.')
        if result.rowcount == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Роль не найдена.')
        return 'OK'

    async def delete_role(self, role_id: uuid.UUID) -> None:
        logger.info(f'delete_role({role_id=})')
        result = await self.session.execute(delete(Role).where(Role.id == role_id))
        await self.session.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Роль не найдена.')


def get_roles_service(
        session: AsyncSession = Depends(get_session),
) -> RolesService:
    return RolesService(session=session)
