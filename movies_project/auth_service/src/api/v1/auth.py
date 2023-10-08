from fastapi import APIRouter, Depends, Response, Request

from models.base import UserAccess, Token
from schemas.auth import UserPassAUTH
from services.authorizations import Auth, get_auth_service

router = APIRouter()


@router.post('/login', description='авторизация пользователя')
async def auth_login(
        response: Response,
        auth: UserPassAUTH,
        auth_service: Auth = Depends(get_auth_service),
) -> UserAccess:
    result = await auth_service.access_user(username=auth.username,
                                            password=auth.password,
                                            response=response)
    await auth_service.create_msg(Token(user_id=result.user_id),
                                  'вход пользователя пользователя в систему')
    return result


@router.post('/logout', description='выход пользователя пользователя')
async def auth_logout(
        response: Response,
        request: Request,
        auth_service: Auth = Depends(get_auth_service),

):
    return await auth_service.logout(response=response, request=request)
