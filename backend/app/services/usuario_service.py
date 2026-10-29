from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
)
from app.models.usuario import Usuario
from app.repositories.empleado_repository import (
    EmpleadoRepository,
)
from app.repositories.rol_repository import (
    RolRepository,
)
from app.repositories.usuario_repository import (
    UsuarioRepository,
)
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioEstadoUpdate,
    UsuarioPasswordUpdate,
    UsuarioRolesUpdate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class UsuarioService:

    @staticmethod
    def obtener(
        db: Session,
        id_usuario: int,
    ) -> dict:

        usuario = UsuarioRepository.get_detalle(
            db,
            id_usuario,
        )

        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        return usuario

    @staticmethod
    def _validar_roles(
        db: Session,
        ids_rol: list[int],
    ) -> list[int]:

        ids = list(
            dict.fromkeys(
                ids_rol
            )
        )

        for id_rol in ids:

            rol = RolRepository.get_by_id(
                db,
                id_rol,
            )

            if rol is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Rol {id_rol} "
                        "no encontrado"
                    ),
                )

            if not rol.activo:
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"El rol {rol.nombre} "
                        "está inactivo"
                    ),
                )

        return ids

    @staticmethod
    def crear(
        db: Session,
        data: UsuarioCreate,
        id_usuario_actor: int,
    ) -> dict:

        empleado = (
            EmpleadoRepository
            .get_by_id(
                db,
                data.id_empleado,
            )
        )

        if empleado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )

        if not empleado.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El empleado está inactivo",
            )

        if (
            UsuarioRepository
            .get_by_empleado(
                db,
                data.id_empleado,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El empleado ya tiene "
                    "un usuario"
                ),
            )

        username = (
            data.username
            .strip()
            .lower()
        )

        if (
            UsuarioRepository
            .get_by_username(
                db,
                username,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El nombre de usuario "
                    "ya existe"
                ),
            )

        ids_rol = (
            UsuarioService
            ._validar_roles(
                db,
                data.ids_rol,
            )
        )

        usuario = Usuario(
            id_empleado=data.id_empleado,
            username=username,
            password_hash=hash_password(
                data.password
            ),
            estado="ACTIVO",
        )

        try:
            db.add(usuario)
            db.flush()

            (
                UsuarioRepository
                .reemplazar_roles(
                    db,
                    usuario.id_usuario,
                    ids_rol,
                )
            )

            resultado = UsuarioService.obtener(
                db,
                usuario.id_usuario,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="CREAR_USUARIO",
                tabla_afectada="usuario",
                id_registro=usuario.id_usuario,
                descripcion=(
                    f"Creación del usuario "
                    f"{username}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible registrar "
                    "el usuario"
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def asignar_roles(
        db: Session,
        id_usuario: int,
        data: UsuarioRolesUpdate,
        id_usuario_actor: int,
    ) -> dict:

        if (
            UsuarioRepository
            .get_by_id(
                db,
                id_usuario,
            )
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        ids = (
            UsuarioService
            ._validar_roles(
                db,
                data.ids_rol,
            )
        )

        datos_anteriores = (
            UsuarioService.obtener(
                db,
                id_usuario,
            )
        )

        try:
            UsuarioRepository.reemplazar_roles(
                db,
                id_usuario,
                ids,
            )

            resultado = UsuarioService.obtener(
                db,
                id_usuario,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="REEMPLAZAR_ROLES_USUARIO",
                tabla_afectada="usuario_rol",
                id_registro=id_usuario,
                descripcion=(
                    f"Reemplazo de roles del "
                    f"usuario {resultado['username']}"
                ),
                datos_anteriores=datos_anteriores,
                datos_nuevos=resultado,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_usuario: int,
        data: UsuarioEstadoUpdate,
        id_usuario_actor: int,
    ) -> dict:

        usuario = UsuarioRepository.get_by_id(
            db,
            id_usuario,
        )

        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        datos_anteriores = (
            UsuarioService.obtener(
                db,
                id_usuario,
            )
        )

        try:
            usuario.estado = data.estado

            db.flush()

            resultado = UsuarioService.obtener(
                db,
                id_usuario,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="CAMBIAR_ESTADO_USUARIO",
                tabla_afectada="usuario",
                id_registro=id_usuario,
                descripcion=(
                    f"Cambio de estado del usuario "
                    f"{resultado['username']}"
                ),
                datos_anteriores=datos_anteriores,
                datos_nuevos=resultado,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def cambiar_password(
        db: Session,
        id_usuario: int,
        data: UsuarioPasswordUpdate,
        id_usuario_actor: int,
    ) -> dict:

        usuario = UsuarioRepository.get_by_id(
            db,
            id_usuario,
        )

        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        datos_usuario = UsuarioService.obtener(
            db,
            id_usuario,
        )

        try:
            usuario.password_hash = hash_password(
                data.nueva_password
            )

            db.flush()

            resultado = UsuarioService.obtener(
                db,
                id_usuario,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="CAMBIAR_PASSWORD_USUARIO",
                tabla_afectada="usuario",
                id_registro=id_usuario,
                descripcion=(
                    f"Cambio de contraseña del usuario "
                    f"{datos_usuario['username']}"
                ),
                datos_nuevos={
                    "id_usuario": id_usuario,
                    "username":
                        datos_usuario["username"],
                    "credencial_actualizada": True,
                },
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def listar(
        db: Session,
        estado: str | None = None,
    ) -> list[dict]:

        ids = UsuarioRepository.list_ids(
            db,
            estado,
        )

        return [
            UsuarioService.obtener(
                db,
                id_usuario,
            )
            for id_usuario in ids
        ]