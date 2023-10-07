import logging

from fastapi import APIRouter, Depends

from schemas.auth import UserPassAUTH
from services.authorizations import Auth, get_auth_service

router = APIRouter()


@router.get('/', description='Стартовая страница auth')
async def read_root() -> str:
    return 'Страница авторизация'


@router.get('/login', description='авторизация пользователя')
async def read_root(
        auth: UserPassAUTH,
) -> str:
    x = await Auth.access_user(username=auth.username, password=auth.password)

    return 'Вы авторизировались'


@router.post('/logout', description='выход пользователя пользователя')
async def auth_user(
        logout: Auth = Depends(Auth.logout)
):
    return 'Пользователь разлогинился'
