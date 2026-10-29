from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.repositories.reporte_repository import (
    ReporteRepository,
)


class ReporteService:

    @staticmethod
    def dashboard(
        db: Session,
    ) -> dict:

        return ReporteRepository.dashboard(
            db
        )

    @staticmethod
    def deuda_por_grado(
        db: Session,
    ) -> list[dict]:

        return (
            ReporteRepository
            .deuda_por_grado(
                db
            )
        )

    @staticmethod
    def deuda_por_estudiante(
        db: Session,
        buscar: str | None,
        offset: int,
        limit: int,
    ) -> list[dict]:

        return (
            ReporteRepository
            .deuda_por_estudiante(
                db=db,
                buscar=buscar,
                offset=offset,
                limit=limit,
            )
        )

    @staticmethod
    def estudiantes_insolventes(
        db: Session,
        buscar: str | None,
        offset: int,
        limit: int,
    ) -> list[dict]:

        return (
            ReporteRepository
            .estudiantes_insolventes(
                db=db,
                buscar=buscar,
                offset=offset,
                limit=limit,
            )
        )

    @staticmethod
    def estado_cuenta(
        db: Session,
        id_estudiante: int,
        id_inscripcion: int | None = None,
    ) -> list[dict]:

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

        if id_inscripcion is not None:
            inscripcion = (
                InscripcionRepository
                .get_by_id(
                    db,
                    id_inscripcion,
                )
            )

            if inscripcion is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=(
                        "Inscripción no encontrada"
                    ),
                )

            if (
                inscripcion.id_estudiante
                != id_estudiante
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "La inscripción no pertenece "
                        "al estudiante"
                    ),
                )

        return (
            ReporteRepository
            .estado_cuenta_estudiante(
                db=db,
                id_estudiante=id_estudiante,
                id_inscripcion=id_inscripcion,
            )
        )