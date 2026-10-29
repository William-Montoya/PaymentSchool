from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.rol import Rol
from app.repositories.permiso_repository import (
    PermisoRepository,
)
from app.repositories.rol_repository import (
    RolRepository,
)
from app.schemas.rol import (
    RolCreate,
    RolEstadoUpdate,
    RolPermisosUpdate,
    RolUpdate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class RolService:

    @staticmethod
    def obtener(
        db: Session,
        id_rol: int,
    ) -> dict:

        rol = RolRepository.get_detalle(
            db,
            id_rol,
        )

        if rol is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado",
            )

        return rol

    @staticmethod
    def crear(
        db: Session,
        data: RolCreate,
        id_usuario_actor: int,
    ) -> dict:

        nombre = (
            data.nombre
            .strip()
            .upper()
        )

        if RolRepository.get_by_nombre(
            db,
            nombre,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El rol ya existe",
            )

        rol = Rol(
            nombre=nombre,
            descripcion=data.descripcion,
            activo=True,
        )

        try:
            db.add(rol)
            db.flush()
            db.refresh(rol)

            resultado = RolService.obtener(
                db,
                rol.id_rol,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="CREAR_ROL",
                tabla_afectada="rol",
                id_registro=rol.id_rol,
                descripcion=(
                    f"Creación del rol {rol.nombre}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El rol ya existe",
            )

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def actualizar(
        db: Session,
        id_rol: int,
        data: RolUpdate,
        id_usuario_actor: int,
    ) -> dict:

        rol = RolRepository.get_by_id(
            db,
            id_rol,
        )

        if rol is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado",
            )

        datos_anteriores = RolService.obtener(
            db,
            id_rol,
        )

        try:
            rol.descripcion = (
                data.descripcion
            )

            db.flush()

            resultado = RolService.obtener(
                db,
                id_rol,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="ACTUALIZAR_ROL",
                tabla_afectada="rol",
                id_registro=id_rol,
                descripcion=(
                    f"Actualización del rol "
                    f"{rol.nombre}"
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
        id_rol: int,
        data: RolEstadoUpdate,
        id_usuario_actor: int,
    ) -> dict:

        rol = RolRepository.get_by_id(
            db,
            id_rol,
        )

        if rol is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado",
            )

        datos_anteriores = RolService.obtener(
            db,
            id_rol,
        )

        try:
            rol.activo = data.activo

            db.flush()

            resultado = RolService.obtener(
                db,
                id_rol,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="CAMBIAR_ESTADO_ROL",
                tabla_afectada="rol",
                id_registro=id_rol,
                descripcion=(
                    f"Cambio de estado del rol "
                    f"{rol.nombre}"
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
    def asignar_permisos(
        db: Session,
        id_rol: int,
        data: RolPermisosUpdate,
        id_usuario_actor: int,
    ) -> dict:

        rol = RolRepository.get_by_id(
            db,
            id_rol,
        )

        if rol is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado",
            )

        ids = list(
            dict.fromkeys(
                data.ids_permiso
            )
        )

        for id_permiso in ids:

            if (
                PermisoRepository
                .get_by_id(
                    db,
                    id_permiso,
                )
                is None
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Permiso {id_permiso} "
                        "no encontrado"
                    ),
                )

        datos_anteriores = RolService.obtener(
            db,
            id_rol,
        )

        try:
            RolRepository.reemplazar_permisos(
                db,
                id_rol,
                ids,
            )

            resultado = RolService.obtener(
                db,
                id_rol,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="REEMPLAZAR_PERMISOS_ROL",
                tabla_afectada="rol_permiso",
                id_registro=id_rol,
                descripcion=(
                    f"Reemplazo de permisos "
                    f"del rol {rol.nombre}"
                ),
                datos_anteriores=datos_anteriores,
                datos_nuevos=resultado,
            )

            db.commit()

        except IntegrityError:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

        return resultado