from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.evaluacion import Evaluacion
from app.repositories.catalogo_academico_repository import (
    CatalogoAcademicoRepository,
)
from app.repositories.evaluacion_repository import (
    EvaluacionRepository,
)
from app.schemas.evaluacion import (
    EvaluacionCreate,
    EvaluacionEstadoUpdate,
)


class EvaluacionService:

    @staticmethod
    def obtener(
        db: Session,
        id_evaluacion: int,
    ) -> Evaluacion:

        evaluacion = EvaluacionRepository.get_by_id(
            db,
            id_evaluacion,
        )

        if evaluacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada",
            )

        return evaluacion

    @staticmethod
    def crear(
        db: Session,
        data: EvaluacionCreate,
    ) -> Evaluacion:

        ciclo = CatalogoAcademicoRepository.get_ciclo(
            db,
            data.id_ciclo,
        )

        if ciclo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciclo escolar no encontrado",
            )

        if ciclo.estado == "CERRADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No pueden crearse evaluaciones "
                    "en un ciclo cerrado"
                ),
            )

        if (
            data.fecha_corte_finanzas
            > data.fecha_evaluacion
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La fecha de corte financiero "
                    "no puede ser posterior "
                    "a la evaluación"
                ),
            )

        existente = (
            EvaluacionRepository
            .get_by_nombre_ciclo(
                db,
                data.id_ciclo,
                data.nombre,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Ya existe una evaluación con "
                    "ese nombre en el ciclo"
                ),
            )

        evaluacion = Evaluacion(
            **data.model_dump()
        )

        try:
            db.add(evaluacion)
            db.commit()
            db.refresh(evaluacion)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible registrar "
                    "la evaluación"
                ),
            )

        return evaluacion

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_evaluacion: int,
        data: EvaluacionEstadoUpdate,
    ) -> Evaluacion:

        evaluacion = EvaluacionService.obtener(
            db,
            id_evaluacion,
        )

        if evaluacion.activo == data.activo:
            return evaluacion

        if data.activo:
            ciclo = (
                CatalogoAcademicoRepository
                .get_ciclo(
                    db,
                    evaluacion.id_ciclo,
                )
            )

            if (
                ciclo is not None
                and ciclo.estado == "CERRADO"
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "No puede activarse una evaluación "
                        "de un ciclo cerrado"
                    ),
                )

        evaluacion.activo = data.activo

        db.commit()
        db.refresh(evaluacion)

        return evaluacion