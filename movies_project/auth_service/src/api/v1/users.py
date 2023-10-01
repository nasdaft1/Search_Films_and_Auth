import uuid
from http import HTTPStatus
from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException

from schemas.base import Page
from schemas.users import UserForCreate, UserInDB
from services.users import get_users_service, UsersService

router = APIRouter()

logger = getLogger('users_api')


@router.post(
    '/create',
    status_code=HTTPStatus.CREATED,
    summary="Создать пользователя",
    tags=['Пользователи'],
    response_model=UserInDB,
)
# @requires_admin
async def create_role(
        user: UserForCreate,
        users_service: UsersService = Depends(get_users_service),
) -> UserInDB:
    return await users_service.create_user(user=user)


@router.get(
    '',
    status_code=HTTPStatus.OK,
    summary='Получить пользователя',
    tags=['Пользователи'],
    response_model=UserInDB,
)
async def get_user(
        *,
        user_id: uuid.UUID,
        users_service: UsersService = Depends(get_users_service),
) -> UserInDB:
    result = await users_service.get_by_id(user_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='user not exist')
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
) -> Page[UserInDB]:
    return await users_service.get_users()


@router.get(
    '/roles',
    status_code=HTTPStatus.OK,
    summary='Получить роли пользователя',
    tags=['Пользователи'],
    response_model=UserInDB,
)
async def get_roles(
        *,
        user_id: uuid.UUID,
        users_service: UsersService = Depends(get_users_service),
) -> UserInDB:
    result = await users_service.get_roles(user_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='user not exist')
    return result
