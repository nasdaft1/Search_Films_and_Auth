import uuid
from http import HTTPStatus
from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from schemas.base import Page
from schemas.roles import RoleForCreate, RoleInDB, RoleForUpdate
from services.roles import get_roles_service, RolesService

logger = getLogger('roles_api')
router = APIRouter()


@router.post(
    '/create',
    status_code=HTTPStatus.CREATED,
    summary='Создать роль',
    tags=['Роли'],
    response_model=RoleInDB,
)
# @requires_admin
async def create_role(
        role: RoleForCreate,
        roles_service: RolesService = Depends(get_roles_service),
) -> RoleInDB:
    return await roles_service.create_role(name=role.name, service_name=role.service_name,
                                           description=role.description)


@router.get(
    '/get',
    status_code=HTTPStatus.OK,
    summary='Получить роль',
    tags=['Роли'],
)
# @requires_admin
async def get_role(
        role_id: Annotated[uuid.UUID, Query(description='Идентификатор роли')],
        roles_service: RolesService = Depends(get_roles_service),
) -> RoleInDB:
    return await roles_service.get_by_id(role_id=role_id)


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    summary='Список ролей',
    tags=['Роли'],
    response_model=Page[RoleInDB],
)
async def get_role(
        roles_service: RolesService = Depends(get_roles_service),
) -> Page[RoleInDB]:
    return await roles_service.get_roles()


@router.put(
    '/update',
    status_code=HTTPStatus.OK,
    summary='Изменить роль',
    tags=['Роли'],
)
# @requires_admin
async def create_role(
        role: RoleForUpdate,
        roles_service: RolesService = Depends(get_roles_service),
) -> str:
    return await roles_service.update_role(role_id=role.id, name=role.name, service_name=role.service_name,
                                           description=role.description)


@router.delete(
    '/delete',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Удалить роль',
    tags=['Роли'],
)
# @requires_admin
async def delete_role(
        role_id: Annotated[uuid.UUID, Query(description='Идентификатор роли')],
        roles_service: RolesService = Depends(get_roles_service),
) -> None:
    await roles_service.delete_role(role_id=role_id)
