from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
)
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    decode_access_token,
)
from app.models.usuario import Usuario
from app.repositories.usuario_repository import (
    UsuarioRepository,
)
from app.services.auth_service import (
    AuthService,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "No se pudieron validar "
            "las credenciales"
        ),
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )


def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    db: Session = Depends(get_db),
) -> Usuario:

    try:
        payload = decode_access_token(
            token
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception()

        id_usuario = int(subject)

        if id_usuario <= 0:
            raise credentials_exception()

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
    ):
        raise credentials_exception()

    usuario = (
        UsuarioRepository
        .get_by_id(
            db,
            id_usuario,
        )
    )

    if usuario is None:
        raise credentials_exception()

    AuthService.validar_acceso(
        db,
        usuario,
    )

    return usuario


CurrentUser = Annotated[
    Usuario,
    Depends(get_current_user),
]

def require_permission(
    permiso: str,
):

    def dependency(
        current_user: Usuario = Depends(
            get_current_user
        ),
        db: Session = Depends(get_db),
    ) -> Usuario:

        tiene_permiso = (
            UsuarioRepository
            .tiene_permiso(
                db=db,
                id_usuario=
                    current_user.id_usuario,
                permiso=permiso,
            )
        )

        if not tiene_permiso:
            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tiene permisos para "
                    "realizar esta operación"
                ),
            )

        return current_user

    return dependency