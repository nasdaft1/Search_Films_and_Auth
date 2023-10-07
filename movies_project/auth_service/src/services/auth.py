from typing import Any

from fastapi import HTTPException, Request, Response

from core.config import Crypt, security_config
from db import redis
from db.redis import con_redis
from models.base import Token
from services.token import create_token
from services.token import read_token


def create_cookies(token: Any, cookie_name, cookie_live, response: Response):
    """Создание cookies"""
    response.set_cookie(key=cookie_name,
                        value=token,
                        httponly=True,  # защищает cookie от JavaScript
                        max_age=cookie_live)


async def check_token(config: Crypt, token_type: bool,
                      request: Request, response: Response) -> Token:
    """
    Обработка токенов и cookies
    :param config:
    :param token_type:
    :param request:
    :param response:
    :return:
    """
    error_status = 200
    cookies_name = config.token_name[int(token_type)]
    token = None
    data = Token()
    try:
        token = request.cookies.get(cookies_name)
        data = read_token(token)
    except HTTPException as error:
        error_status = error.status_code
        if error_status != 401 and token_type:
            raise HTTPException(status_code=403, detail="В доступе отказано авторизуйтесь")
    # Проверяем access token что не в black_list
    if token is None or data is None:
        raise HTTPException(status_code=403, detail="В доступе отказано авторизуйтесь")
    black_list = redis.get_value(token)

    match black_list, token_type, error_status:
        case True, _, _:
            # token находится в Black list
            raise HTTPException(status_code=403, detail="В доступе отказано авторизуйтесь")
        case None, False, 401:
            # access не в black_list, необходимо пересоздать access_token время использования закончилось
            await check_token(config, True, request, response)

        case None, False, 200:
            # access не в black_list выполняем далее программу
            return data
        case None, True, _:
            # refresh не в black_list пересоздать токен access и refresh
            for index in range(2):
                create_cookies(
                    token=create_token(data=data, time_live=config.token_live[index]),
                    cookie_name=config.token_name[index],
                    cookie_live=config.cookie_live[index],
                    response=response)
            return data
            # проверить есть ли доступ к странице в соответствии с ролью


def access(role=list[str]):
    """Проверка токенов и роли доступа """

    async def token(request: Request, response: Response):
        user_data = await check_token(config=security_config,
                                      token_type=False,
                                      request=request,
                                      response=response)
        if user_data is not None:
            if security_config.admin_role_name in user_data.roles \
                    or set(user_data.roles) & set(role):
                return user_data
        raise HTTPException(status_code=401, detail="У вас недостаточные права для ресурса")

    return token
