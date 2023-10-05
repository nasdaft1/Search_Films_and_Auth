import logging

from functools import wraps
from fastapi import Request


def roles_required(roles_list: list[str] | None = None):
    def decorator(function):
        @wraps(function)
        # async def wrapper(*args, **kwargs, ):
        async def wrapper(*args, requst: Request, **kwargs, ):
            logging.debug(args)
            logging.debug(kwargs)
            logging.debug(requst)
            request = kwargs.get('request')
            logging.debug('2222222222222222222222222222222222222222')
            # logging.debug(f'Request to the server от ip={request.url.components.path}')

            # user: UserInDb = getattr(kwargs.get('request'), 'user_data')
            # if not user:
            #     raise AuthException(
            #         'This operation is forbidden for you',
            #         status_code=status.HTTP_403_FORBIDDEN,
            #     )
            # has_required_roles = bool(
            #     set(roles_list).intersection(set(user.roles_list))
            # )
            # if not has_required_roles:
            #     raise AuthException(
            #         'This operation is forbidden for you',
            #         status_code=status.HTTP_403_FORBIDDEN,
            #     )
            return await function(*args, **kwargs)

        return wrapper

    return decorator


requires_admin = roles_required(roles_list=['admin'])
