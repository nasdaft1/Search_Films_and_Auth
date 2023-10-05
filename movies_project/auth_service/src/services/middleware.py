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


# response.set_cookie(key=config_token.token_name,
#                         value=token,
#                         httponly=True,  # защищает cookie от JavaScript
#                         max_age=config_token.cookie_max_age)

async def middleware(request: Request, call_next: Any) -> Any:
    """Обработка всех запросов и отбор их по ip"""
    # logging.debug(f'Request to the server от ip={request.url.components.path}')
    # logging.debug(f'Request to the server от ip={request.get("tags", [])}')
    # logging.debug(f'Request to the server от ip={request.method}')
    # logging.debug(f'Request to the server от ip={request.query_params}')
    #
    # logging.debug(f'Request to the server от tags={request.__dict__}')
    # logging.debug(f'Request to the server от tags={request.headers}')
    # token_at = request.cookies.get(security_config.token_name_session)
    # try:
    #     result = read_token(token_at)
    # except HTTPException as error:
    #     pass

    # получение токена AT
    # проверка токена на валидность
    # проверка токена blacklist
    #
    # проверка роли в базе данных редис

    # result = await ServiceBlackList().check_black_list_ip(request.client.host)
    # if result is True:
    #     return HTMLResponse(status_code=403, content="access denied")

    logging.debug('11111111111111111111111111111111111111111111')
    logging.debug(request.__dict__)
    logging.debug(call_next.__dict__)
    response = await call_next(request)
    logging.debug(response.__dict__)
    logging.debug('33333333333333333333333333333333333333333333')
    return response
