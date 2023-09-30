from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession


class BaseService(ABC):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session
