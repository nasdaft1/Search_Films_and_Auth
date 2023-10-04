import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class RoleForCreate(BaseModel):
    name: Annotated[str, Query(description='Название роли. До 20 символов.', max_length=20)]
    service_name: Annotated[str, Query(description='Уникальное техническое название роли. До 20 символов.',
                                       max_length=20)]
    description: Annotated[str | None, Query(description='Описание роли. До 120 символов.', max_length=120)]

    def __repr__(self) -> str:
        return f'<RoleCreate(name={self.name}, service_name={self.service_name}>'


class RoleForUpdate(RoleForCreate):
    id: uuid.UUID

    def __repr__(self) -> str:
        return f'<RoleForUpdate(id={self.id}, name={self.name}, service_name={self.service_name}>'


class RoleInDB(RoleForCreate):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

    def __repr__(self) -> str:
        return f'<RoleInDB(id={self.id}, name={self.name}, service_name={self.service_name}>'
