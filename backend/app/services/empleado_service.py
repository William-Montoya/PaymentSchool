from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.empleado import Empleado
from app.repositories.empleado_repository import (
    EmpleadoRepository,
)
from app.schemas.empleado import (
    EmpleadoCreate,
    EmpleadoEstadoUpdate,
    EmpleadoUpdate,
)


class EmpleadoService:

    @staticmethod
    def obtener(
        db: Session,
        id_empleado: int,
    ) -> Empleado:

        empleado = EmpleadoRepository.get_by_id(
            db,
            id_empleado,
        )

        if empleado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )

        return empleado

    @staticmethod
    def crear(
        db: Session,
        data: EmpleadoCreate,
    ) -> Empleado:

        empleado = Empleado(
            **data.model_dump()
        )

        db.add(empleado)
        db.commit()
        db.refresh(empleado)

        return empleado

    @staticmethod
    def actualizar(
        db: Session,
        id_empleado: int,
        data: EmpleadoUpdate,
    ) -> Empleado:

        empleado = EmpleadoService.obtener(
            db,
            id_empleado,
        )

        cambios = data.model_dump(
            exclude_unset=True
        )

        for campo, valor in cambios.items():
            setattr(
                empleado,
                campo,
                valor,
            )

        db.commit()
        db.refresh(empleado)

        return empleado

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_empleado: int,
        data: EmpleadoEstadoUpdate,
    ) -> Empleado:

        empleado = EmpleadoService.obtener(
            db,
            id_empleado,
        )

        empleado.activo = data.activo

        db.commit()
        db.refresh(empleado)

        return empleado