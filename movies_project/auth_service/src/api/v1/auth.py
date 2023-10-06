import logging

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from schemas.auth import UserPassAUTH
from services.authorizations import Auth, get_auth_service

router = APIRouter()


@router.get('/', description='Стартовая страница auth')
async def read_root() -> str:
    return 'Страница авторизация'


@router.get('/login', description='авторизация пользователя')
async def read_root() -> str:
    logging.info('Добро пожаловать в Файловое хранилище')
    return 'Добро пожаловать в Файловое хранилище'


@router.post('/logout', description='выход пользователя пользователя')
async def auth_user(
        response: Response,
        auth: UserPassAUTH,
        access_user: Auth = Depends(get_auth_service)
):
    # user_id, role_id = await access_user.access_user(
    #     username=auth.username, password=auth.password)
    # token = auto.create_access_token(user_id=user_id, role_id=role_id)
    # создаем cookies и отправляем его
    # return [user_id, role_id]
    return 1
