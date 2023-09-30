import uuid

from sqlalchemy import Boolean, Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# Импортируем базовый класс для моделей.
Base = declarative_base()


def generator() -> UUID:
    return uuid.uuid4()


class AuthSchema(Base):
    __abstract__ = True
    __table_args__ = {'schema': 'auth'}


class User(AuthSchema):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    username = Column(String(50), unique=True)
    password_hash = Column(String(64))
    full_name = Column(String(50))
    is_deleted = Column(Boolean, default=False)
    email = Column(String(50), unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Api(AuthSchema):
    __tablename__ = "api"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    url = Column(String(50), unique=True)
    url_validation = Column(String(50), unique=True)
    description = Column(String(120))
    created_at = Column(DateTime, server_default=func.now())


class ApiRole(AuthSchema):
    __tablename__ = "api_role"
    api_id = Column(UUID, ForeignKey('auth.api.id'), primary_key=True)
    role_id = Column(UUID, ForeignKey('auth.role.id'), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())


class UserRole(AuthSchema):
    __tablename__ = "user_role"
    user_id = Column(UUID, ForeignKey('auth.user.id'), primary_key=True)
    role_id = Column(UUID, ForeignKey('auth.role.id'), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())


class Role(AuthSchema):
    __tablename__ = "role"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    name = Column(String(20), unique=True)
    service_name = Column(String(20), unique=True)
    description = Column(String(120))
    created_at = Column(DateTime, server_default=func.now())


class History(AuthSchema):
    __tablename__ = "history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    user_id = Column(UUID, ForeignKey('auth.user.id'))
    message = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
