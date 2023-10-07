import asyncio

import typer

from db.postgres import async_session
from schemas.users import UserForCreate
from services.roles import get_roles_service
from services.users import get_users_service

app = typer.Typer()


async def create_user_async(username: str, password: str, full_name: str, email: str, role: str = 'user'):
    async with async_session() as session:
        users_service = get_users_service(session)
        roles_service = get_roles_service(session)

        user_in_db = await users_service.get_by_username(username=username)
        if user_in_db:
            return f'Пользователь с таким логином уже существует. id={user_in_db.id}'

        user_in_db = await users_service.get_by_email(email=email)
        if user_in_db:
            return f'Пользователь с такой почтой уже существует. id={user_in_db.id}'

        user = UserForCreate(username=username, password=password, full_name=full_name, email=email)
        user_in_db = await users_service.create_user(user=user)

        role_in_db = await roles_service.get_by_name(name=role)
        if not role_in_db:
            role_in_db = await roles_service.create_role(name=role, service_name=role, description='Created by CLI')

        await users_service.add_role(user_id=user_in_db.id, role=role_in_db)
        return f'Пользователь создан. id={user_in_db.id}'


@app.command()
def create_user(username: str = typer.Option(None, prompt='Enter username'),
                password: str = typer.Option(None, prompt='Enter password', hide_input=True,
                                             confirmation_prompt=True),
                full_name: str = typer.Option(None, prompt='Enter full name'),
                email: str = typer.Option(None, prompt='Enter email'),
                role: str = typer.Option('admin', prompt='Enter role')):
    """
    Create a new user.

    Arguments:
    - username: The username for the new user.
    - password: The password for the new user.
    - full_name: The full name of the user.
    - email: The email address of the user.
    - role: The role for the new user (default is 'admin').
    """

    result = asyncio.run(create_user_async(username=username, password=password, full_name=full_name, email=email,
                                           role=role))
    print(result)


if __name__ == "__main__":
    app()
