from typing import Literal

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str

    token_type: Literal["bearer"] = "bearer"

    expires_in: int


class TokenPayload(BaseModel):
    sub: str

    type: Literal["access"]

    iat: int
    exp: int