from datetime import datetime

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.exc import (
    IntegrityError,
)
from sqlalchemy.orm import Session

from app.models.estudiante import (
    Estudiante,
)
from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.schemas.estudiante import (
    EstudianteCreate,
    EstudianteEstadoUpdate,
    EstudianteUpdate,
)


class EstudianteService:

    @staticmethod
    def obtener(
        db: Session,
        id_estudiante: int,
    ) -> Estudiante:

        estudiante = (
            EstudianteRepository
            .get_by_id(
                db,
                id_estudiante,
            )
        )

        if estudiante is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Estudiante no encontrado"
                ),
            )

        return estudiante

    @staticmethod
    def listar(
        db: Session,
        offset: int = 0,
        limit: int = 50,
        estado: str | None = None,
        buscar: str | None = None,
    ) -> list[Estudiante]:

        return (
            EstudianteRepository
            .list(
                db=db,
                offset=offset,
                limit=limit,
                estado=estado,
                buscar=buscar,
            )
        )

    @staticmethod
    def crear(
        db: Session,
        data: EstudianteCreate,
    ) -> Estudiante:

        if (
            data.cui
            and
            EstudianteRepository
            .get_by_cui(
                db,
                data.cui,
            )
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "El CUI ya está "
                    "registrado"
                ),
            )

        estudiante = Estudiante(
            **data.model_dump()
        )

        try:
            (
                EstudianteRepository
                .create(
                    db,
                    estudiante,
                )
            )

            db.commit()
            db.refresh(estudiante)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible registrar "
                    "el estudiante"
                ),
            )

        return estudiante

    @staticmethod
    def actualizar(
        db: Session,
        id_estudiante: int,
        data: EstudianteUpdate,
    ) -> Estudiante:

        estudiante = (
            EstudianteService
            .obtener(
                db,
                id_estudiante,
            )
        )

        cambios = data.model_dump(
            exclude_unset=True
        )

        if cambios.get("cui"):
            existente = (
                EstudianteRepository
                .get_by_cui(
                    db,
                    cambios["cui"],
                )
            )

            if (
                existente
                and
                existente.id_estudiante
                != id_estudiante
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "El CUI ya está "
                        "registrado"
                    ),
                )

        for campo, valor in cambios.items():
            setattr(
                estudiante,
                campo,
                valor,
            )

        estudiante.actualizado_en = (
            datetime.now()
        )

        try:
            (
                EstudianteRepository
                .save(
                    db,
                    estudiante,
                )
            )

            db.commit()
            db.refresh(estudiante)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible actualizar "
                    "el estudiante"
                ),
            )

        return estudiante

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_estudiante: int,
        data: EstudianteEstadoUpdate,
    ) -> Estudiante:

        estudiante = (
            EstudianteService
            .obtener(
                db,
                id_estudiante,
            )
        )

        estudiante.estado = (
            data.estado
        )

        estudiante.actualizado_en = (
            datetime.now()
        )

        db.commit()
        db.refresh(estudiante)

        return estudiante