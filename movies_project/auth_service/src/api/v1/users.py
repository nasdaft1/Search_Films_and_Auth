import uuid
from http import HTTPStatus
from logging import getLogger

from fastapi import APIRouter, Depends

from schemas.base import Page
from schemas.roles import RoleInDB
from schemas.users import (
    UserForCreate,
    UserForUpdate,
    UserInDB,
    HistoryInDB,
    HistoryForCreate,
    UserHistory
)
from services.roles import RolesService, get_roles_service
from services.users import UsersService, get_users_service
from services.auth import access

router = APIRouter()

logger = getLogger('users_api')


@router.post(
    '/create',
    status_code=HTTPStatus.CREATED,
    summary='Создание пользователя',
    tags=['Пользователи'],
    response_model=UserInDB,
)
async def create_role(
        user: UserForCreate,
        users_service: UsersService = Depends(get_users_service),
        auth=Depends(access(['self'])),
) -> UserInDB:
    return await users_service.create_user(user=user)


@router.get(
    '/get',
    status_code=HTTPStatus.OK,
    summary='Получение пользователя',
    tags=['Пользователи'],
    response_model=UserInDB,
)
async def get_user(
        *,
        user_id: uuid.UUID,
        users_service: UsersService = Depends(get_users_service),
        auth=Depends(access(['self'])),
) -> UserInDB:
    result = await users_service.get_by_id(user_id)
    return result


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    summary='Список пользователей',
    tags=['Пользователи'],
    response_model=Page[UserInDB],
)
async def get_users(
        users_service: UsersService = Depends(get_users_service),
        auth=Depends(access(['self'])),
) -> Page[UserInDB]:
    return await users_service.get_users()


@router.put(
    '/update',
    status_code=HTTPStatus.CREATED,
    summary='Обновление информации авторизованного пользователя',
    tags=['Пользователи'],
    response_model=str,
)
async def update_user(
        user: UserForUpdate,
        users_service: UsersService = Depends(get_users_service),
        auth=Depends(access(['self'])),
) -> str:
    return await users_service.update_user(user=user)


@router.get(
    '/roles',
    status_code=HTTPStatus.OK,
    summary='Получение ролей пользователя',
    tags=['Пользователи'],
    response_model=list[RoleInDB],
)
async def get_roles(
        *,
        user_id: uuid.UUID,
        users_service: UsersService = Depends(get_users_service),
        auth=Depends(access(['self'])),
) -> list[RoleInDB]:
    return await users_service.get_roles(user_id)


@router.get(
    '/history',
    status_code=HTTPStatus.OK,
    summary='Получение истории действий',
    tags=['Пользователи'],
    response_model=list[UserHistory],
)
async def get_history(
        *,
        user_id: uuid.UUID,
        users_service: UsersService = Depends(get_users_service),
        auth=Depends(access(['self'])),
) -> list[UserHistory]:
    return await users_service.get_history(user_id)


@router.post(
    '/add_history',
    status_code=HTTPStatus.CREATED,
    summary='Добавление действия в историю',
    tags=['Пользователи'],
    response_model=HistoryInDB,
)
async def add_history(
        *,
        history: HistoryForCreate,
        users_service: UsersService = Depends(get_users_service),
        auth=Depends(access(['self'])),
) -> HistoryInDB:
    return await users_service.add_history(history)


@router.post(
    '/add_role',
    status_code=HTTPStatus.CREATED,
    summary='Добавление роли пользователю',
    tags=['Пользователи'],
    response_model=str,
)
async def add_role(
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        users_service: UsersService = Depends(get_users_service),
        roles_service: RolesService = Depends(get_roles_service),
        auth=Depends(access(['self'])),
) -> str:
    role = await roles_service.get_by_id(role_id=role_id)
    result = await users_service.add_role(user_id=user_id, role=role)
    return result


@router.delete(
    '/remove_role',
    status_code=HTTPStatus.CREATED,
    summary='Удаление роли у пользователя',
    tags=['Пользователи'],
)
async def remove_role(
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        users_service: UsersService = Depends(get_users_service),
        roles_service: RolesService = Depends(get_roles_service),
        auth=Depends(access(['self'])),
) -> None:
    role = await roles_service.get_by_id(role_id=role_id)
    await users_service.remove_role(user_id=user_id, role=role)
