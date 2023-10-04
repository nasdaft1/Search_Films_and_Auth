import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

from src.core.config import config

Base = declarative_base()


def generator() -> UUID:
    return uuid.uuid4()


class AuthSchema(Base):
    __abstract__ = True
    __table_args__ = {'schema': config.auth_schema}


class User(AuthSchema):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    username = Column(String(50), unique=True)
    password_hash = Column(String(128))
    full_name = Column(String(50))
    email = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    roles = relationship("Role", secondary="auth.user_role", backref="users")
    history = relationship("History", backref="user")


class Api(AuthSchema):
    __tablename__ = "api"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    url = Column(String(50), unique=True)
    url_validation = Column(String(50), unique=True)
    description = Column(String(120))
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiRole(AuthSchema):
    __tablename__ = "api_role"
    api_id = Column(UUID(as_uuid=True), ForeignKey('auth.api.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('auth.role.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRole(AuthSchema):
    __tablename__ = "user_role"
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.user.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('auth.role.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Role(AuthSchema):
    __tablename__ = "role"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    name = Column(String(20), unique=True)
    service_name = Column(String(20), unique=True)
    description = Column(String(120))
    created_at = Column(DateTime, default=datetime.utcnow)


class History(AuthSchema):
    __tablename__ = "history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generator)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.user.id'))
    message = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
