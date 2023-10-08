from pydantic import BaseModel


class UserAccess(BaseModel):
    username: str | None = None
    roles: list[str] | None = None


class Token(BaseModel):
    user_id: str | None = None
    roles: list[str] | None = None


class GetToken(Token):
    expiration_timestamp: str
