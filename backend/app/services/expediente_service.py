from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.expediente import Expediente
from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.repositories.expediente_repository import (
    ExpedienteRepository,
)
from app.schemas.expediente import (
    ExpedienteCreate,
    ExpedienteUpdate,
)


class ExpedienteService:

    @staticmethod
    def crear(
        db: Session,
        data: ExpedienteCreate,
    ) -> dict:

        estudiante = (
            EstudianteRepository
            .get_by_id(
                db,
                data.id_estudiante,
            )
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        existente = (
            ExpedienteRepository
            .get_by_estudiante(
                db,
                data.id_estudiante,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El estudiante ya posee "
                    "un expediente"
                ),
            )

        expediente = Expediente(
            **data.model_dump()
        )

        try:
            db.add(expediente)
            db.commit()
            db.refresh(expediente)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible crear "
                    "el expediente"
                ),
            )

        return (
            ExpedienteRepository
            .get_detalle(
                db,
                expediente.id_expediente,
            )
        )

    @staticmethod
    def obtener(
        db: Session,
        id_expediente: int,
    ) -> dict:

        expediente = (
            ExpedienteRepository
            .get_detalle(
                db,
                id_expediente,
            )
        )

        if expediente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expediente no encontrado",
            )

        return expediente

    @staticmethod
    def obtener_por_estudiante(
        db: Session,
        id_estudiante: int,
    ) -> dict:

        estudiante = (
            EstudianteRepository
            .get_by_id(
                db,
                id_estudiante,
            )
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        expediente = (
            ExpedienteRepository
            .get_by_estudiante(
                db,
                id_estudiante,
            )
        )

        if expediente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "El estudiante todavía "
                    "no posee expediente"
                ),
            )

        return (
            ExpedienteRepository
            .get_detalle(
                db,
                expediente.id_expediente,
            )
        )

    @staticmethod
    def actualizar(
        db: Session,
        id_expediente: int,
        data: ExpedienteUpdate,
    ) -> dict:

        expediente = (
            ExpedienteRepository
            .get_by_id(
                db,
                id_expediente,
            )
        )

        if expediente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expediente no encontrado",
            )

        cambios = data.model_dump(
            exclude_unset=True
        )

        for campo, valor in cambios.items():
            setattr(
                expediente,
                campo,
                valor,
            )

        expediente.actualizado_en = (
            datetime.now()
        )

        db.commit()
        db.refresh(expediente)

        return (
            ExpedienteRepository
            .get_detalle(
                db,
                id_expediente,
            )
        )