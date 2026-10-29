from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.carrera import Carrera
from app.models.carrera_ciclo import CarreraCiclo
from app.models.ciclo_escolar import CicloEscolar
from app.models.grado import Grado
from app.repositories.catalogo_academico_repository import (
    CatalogoAcademicoRepository,
)
from app.schemas.catalogo_academico import (
    CarreraCicloCreate,
    CarreraCreate,
    CicloCreate,
    GradoCreate,
)


class CatalogoAcademicoService:

    @staticmethod
    def crear_ciclo(
        db: Session,
        data: CicloCreate,
    ) -> CicloEscolar:

        if data.fecha_fin < data.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La fecha de finalización no puede "
                    "ser anterior a la fecha de inicio"
                ),
            )

        existente = (
            CatalogoAcademicoRepository
            .get_ciclo_by_nombre(
                db,
                data.nombre,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un ciclo con ese nombre",
            )

        ciclo = CicloEscolar(
            **data.model_dump()
        )

        try:
            db.add(ciclo)
            db.commit()
            db.refresh(ciclo)

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible registrar el ciclo",
            )

        return ciclo

    @staticmethod
    def crear_carrera(
        db: Session,
        data: CarreraCreate,
    ) -> Carrera:

        existente = (
            CatalogoAcademicoRepository
            .get_carrera_by_nombre(
                db,
                data.nombre,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una carrera con ese nombre",
            )

        carrera = Carrera(
            **data.model_dump()
        )

        try:
            db.add(carrera)
            db.commit()
            db.refresh(carrera)

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible registrar la carrera",
            )

        return carrera

    @staticmethod
    def crear_carrera_ciclo(
        db: Session,
        data: CarreraCicloCreate,
    ) -> CarreraCiclo:

        carrera = (
            CatalogoAcademicoRepository
            .get_carrera(
                db,
                data.id_carrera,
            )
        )

        if carrera is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrera no encontrada",
            )

        ciclo = (
            CatalogoAcademicoRepository
            .get_ciclo(
                db,
                data.id_ciclo,
            )
        )

        if ciclo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciclo escolar no encontrado",
            )

        existente = (
            CatalogoAcademicoRepository
            .get_carrera_ciclo_existente(
                db,
                data.id_carrera,
                data.id_ciclo,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "La carrera ya está asociada "
                    "a este ciclo escolar"
                ),
            )

        carrera_ciclo = CarreraCiclo(
            **data.model_dump()
        )

        try:
            db.add(carrera_ciclo)
            db.commit()
            db.refresh(carrera_ciclo)

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible asociar la carrera "
                    "al ciclo escolar"
                ),
            )

        return carrera_ciclo

    @staticmethod
    def crear_grado(
        db: Session,
        data: GradoCreate,
    ) -> Grado:

        carrera_ciclo = (
            CatalogoAcademicoRepository
            .get_carrera_ciclo(
                db,
                data.id_carrera_ciclo,
            )
        )

        if carrera_ciclo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrera/ciclo no encontrada",
            )

        existente = (
            CatalogoAcademicoRepository
            .get_grado_by_nombre(
                db,
                data.id_carrera_ciclo,
                data.nombre,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Ya existe ese grado para "
                    "la carrera/ciclo seleccionada"
                ),
            )

        grado = Grado(
            **data.model_dump()
        )

        try:
            db.add(grado)
            db.commit()
            db.refresh(grado)

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible registrar el grado",
            )

        return grado