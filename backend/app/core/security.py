from datetime import (
    datetime,
    timedelta,
    timezone,
)
from typing import Any

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings


_password_hash = PasswordHash.recommended()


# ============================================================
# PASSWORDS
# ============================================================

def hash_password(
    password: str,
) -> str:
    return _password_hash.hash(
        password
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return _password_hash.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# JWT
# ============================================================

def create_access_token(
    subject: int | str,
) -> str:

    now = datetime.now(
        timezone.utc
    )

    expires_at = (
        now
        + timedelta(
            minutes=
                settings.jwt_access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(subject),
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=
            settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
) -> dict[str, Any]:

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[
            settings.jwt_algorithm
        ],
    )

    if payload.get("type") != "access":
        raise InvalidTokenError(
            "Tipo de token inválido"
        )

    subject = payload.get("sub")

    if not subject:
        raise InvalidTokenError(
            "Token sin usuario"
        )

    return payload