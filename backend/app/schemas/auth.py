from pydantic import BaseModel, Field


class SetupBody(BaseModel):
    username: str = Field(default="admin", min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=256)


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class AuthStatus(BaseModel):
    initialized: bool
    authenticated: bool
    allow_insecure: bool
    username: str | None = None
    role: str | None = None
    permissions: list[str] = []
