import logging
from typing import Any
from core.config import security_config
from services.token import read_token

from fastapi import HTTPException, Request
from db.redis import con_redis


async def check_token(request: Request, cookies_name: list[str], token_type: bool):
    """
    Обработка токенов и cookies
    :param request:
    :param cookies_name:
    :param token_type: True - сессии False - refresh
    :return:
    """
    error_status = 200
    try:
        token = request.cookies.get(cookies_name)
        result = read_token(token)
    except HTTPException as error:
        error_status = error.status_code
        if error_status != 401 and token_type:
            raise HTTPException(status_code=403, detail="В доступе отказано авторизуйтесь")
    # Проверяем access token что не в black_list
    black_list = con_redis.get(token)
    match black_list, token_type, error_status:
        case True, _, _:
            # В доступе отказано
            # return RedirectResponse(url="/new-url")
            raise HTTPException(status_code=403, detail="В доступе отказано авторизуйтесь")
        case None, True, 401:
            # access не в black_list
            check_token(request, cookies_name, )

        case None, True, 200:
            # access не в black_list
            pass
        case None, False, _:
            # refresh не в black_list пересоздать токен
            pass

        # error.status_code
        # return RedirectResponse(url="/new-url")


def access(role=list[str]):
    async def token(request: Request):
        logging.debug('11111111111111111111111')
        logging.debug(role)
        logging.debug(request.url)
        pass

    return token


# response.set_cookie(key=config_token.token_name,
#                         value=token,
#                         httponly=True,  # защищает cookie от JavaScript
#                         max_age=config_token.cookie_max_age)