import logging

from fastapi import APIRouter, Depends, Response

from models.base import UserAccess
from schemas.auth import UserPassAUTH
from services.authorizations import Auth, get_auth_service

router = APIRouter()


@router.get('/', description='Стартовая страница auth')
async def read_root() -> str:
    return 'Страница авторизация'


@router.post('/login', description='авторизация пользователя')
async def read_root(
        response: Response,
        auth: UserPassAUTH,
        auth_service=Depends(get_auth_service),
) -> UserAccess:
    return await auth_service.access_user(username=auth.username,
                                          password=auth.password,
                                          response=response)


@router.post('/logout', description='выход пользователя пользователя')
async def auth_user(
        logout: Auth = Depends(Auth.logout)
):
    return logout
