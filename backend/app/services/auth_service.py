from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.models.usuario import Usuario
from app.repositories.auth_repository import (
    AuthRepository,
)
from app.repositories.empleado_repository import (
    EmpleadoRepository,
)


class AuthService:

    # ============================================================
    # VALIDAR ACCESO DEL USUARIO
    # ============================================================

    @staticmethod
    def validar_acceso(
        db: Session,
        usuario: Usuario,
    ) -> None:

        # --------------------------------------------------------
        # Estado del usuario
        # --------------------------------------------------------

        if usuario.estado == "INACTIVO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "El usuario se encuentra inactivo"
                ),
            )

        if usuario.estado == "BLOQUEADO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "El usuario se encuentra bloqueado"
                ),
            )

        if usuario.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "El usuario no puede acceder "
                    "al sistema"
                ),
            )

        # --------------------------------------------------------
        # Empleado asociado
        # --------------------------------------------------------

        if usuario.id_empleado is None:
            return

        empleado = (
            EmpleadoRepository
            .get_by_id(
                db,
                usuario.id_empleado,
            )
        )

        if empleado is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "El usuario no tiene un "
                    "empleado válido asociado"
                ),
            )

        if not empleado.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "El empleado asociado "
                    "se encuentra inactivo"
                ),
            )

    # ============================================================
    # LOGIN
    # ============================================================

    @staticmethod
    def login(
        db: Session,
        username: str,
        password: str,
    ) -> dict:

        username = username.strip()

        # --------------------------------------------------------
        # Buscar usuario
        # --------------------------------------------------------

        usuario = (
            AuthRepository
            .get_by_username(
                db,
                username,
            )
        )

        # --------------------------------------------------------
        # Usuario inexistente
        # --------------------------------------------------------

        if usuario is None:
            raise HTTPException(
                status_code=
                    status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Usuario o contraseña incorrectos"
                ),
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        # --------------------------------------------------------
        # Validar contraseña
        # --------------------------------------------------------

        try:
            password_valida = (
                verify_password(
                    password,
                    usuario.password_hash,
                )
            )

        except Exception:
            password_valida = False

        if not password_valida:
            raise HTTPException(
                status_code=
                    status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Usuario o contraseña incorrectos"
                ),
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        # --------------------------------------------------------
        # Validar usuario + empleado
        # --------------------------------------------------------

        AuthService.validar_acceso(
            db,
            usuario,
        )

        # --------------------------------------------------------
        # Actualizar último acceso
        # --------------------------------------------------------

        try:
            (
                AuthRepository
                .actualizar_ultimo_acceso(
                    db,
                    usuario,
                )
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        # --------------------------------------------------------
        # Crear JWT
        # --------------------------------------------------------

        access_token = (
            create_access_token(
                usuario.id_usuario
            )
        )

        # --------------------------------------------------------
        # Respuesta
        # --------------------------------------------------------

        return {
            "access_token": access_token,

            "token_type": "bearer",

            "expires_in": (
                settings
                .jwt_access_token_expire_minutes
                * 60
            ),
        }