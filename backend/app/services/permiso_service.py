from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.permiso import Permiso
from app.repositories.permiso_repository import (
    PermisoRepository,
)
from app.schemas.permiso import (
    PermisoCreate,
    PermisoUpdate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class PermisoService:

    @staticmethod
    def obtener(
        db: Session,
        id_permiso: int,
    ) -> Permiso:

        permiso = PermisoRepository.get_by_id(
            db,
            id_permiso,
        )

        if permiso is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permiso no encontrado",
            )

        return permiso

    @staticmethod
    def _to_dict(
        permiso: Permiso,
    ) -> dict:
        return {
            "id_permiso": permiso.id_permiso,
            "nombre": permiso.nombre,
            "descripcion": permiso.descripcion,
        }

    @staticmethod
    def crear(
        db: Session,
        data: PermisoCreate,
        id_usuario_actor: int,
    ) -> Permiso:

        nombre = (
            data.nombre
            .strip()
            .upper()
        )

        existente = (
            PermisoRepository
            .get_by_nombre(
                db,
                nombre,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El permiso ya existe",
            )

        permiso = Permiso(
            nombre=nombre,
            descripcion=data.descripcion,
        )

        try:
            db.add(permiso)
            db.flush()
            db.refresh(permiso)

            resultado = PermisoService._to_dict(
                permiso
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="CREAR_PERMISO",
                tabla_afectada="permiso",
                id_registro=permiso.id_permiso,
                descripcion=(
                    f"Creación del permiso {permiso.nombre}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El permiso ya existe",
            )

        except Exception:
            db.rollback()
            raise

        return permiso

    @staticmethod
    def actualizar(
        db: Session,
        id_permiso: int,
        data: PermisoUpdate,
        id_usuario_actor: int,
    ) -> Permiso:

        permiso = PermisoService.obtener(
            db,
            id_permiso,
        )

        datos_anteriores = PermisoService._to_dict(
            permiso
        )

        try:
            permiso.descripcion = data.descripcion

            db.flush()
            db.refresh(permiso)

            resultado = PermisoService._to_dict(
                permiso
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario_actor,
                modulo="SEGURIDAD",
                accion="ACTUALIZAR_PERMISO",
                tabla_afectada="permiso",
                id_registro=id_permiso,
                descripcion=(
                    f"Actualización del permiso {permiso.nombre}"
                ),
                datos_anteriores=datos_anteriores,
                datos_nuevos=resultado,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        return permiso
