import logging
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import JWTError, jwt

from core.config import security_config
from models.base import Token


def create_token(data: Token, time_live: int):
    """
    Создаем token c временем пользования
    :param name_token: str имя создаваемого токена
    :param date: dict данные передаваемыми в token
    :param time_live: int время жизни token в секундах
    :param response: Response
    :return:
    """
    to_encode = dict(data)
    expire = datetime.utcnow() + timedelta(seconds=time_live)
    to_encode.update({'exp': expire})
    logging.debug(f' now ={datetime.utcnow()} end date token {expire}')
    logging.debug(to_encode)
    return jwt.encode(to_encode, security_config.secret_key, algorithm=security_config.algorithm)


async def read_token(token: str) -> Token:
    """
    Чтение данных из токена
    :param token: str
    :return: [user_id: str | None = None, roles: list[str] | None = None, expiration_timestamp: str]
    """
    try:
        if token is None:
            raise HTTPException(status_code=404, detail='Не найден токен')

        payload = jwt.decode(token, security_config.secret_key, algorithms=[security_config.algorithm])
        info = payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Токен истек')
    except JWTError as error:
        logging.debug(error)
        raise HTTPException(status_code=400, detail='Недействительный токен')
    return Token(**info,
                 expiration_timestamp=payload.get('exp')  # извлечение времени истечения токена
                 )
