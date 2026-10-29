from __future__ import annotations
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.precio_carrera import PrecioCarrera


class PrecioCarreraRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_precio: int,
    ) -> PrecioCarrera | None:
        return db.get(
            PrecioCarrera,
            id_precio,
        )

    @staticmethod
    def list(
        db: Session,
        id_carrera_ciclo: int | None = None,
        id_grado: int | None = None,
        tipo: str | None = None,
        activo: bool | None = None,
    ) -> list[PrecioCarrera]:

        stmt = select(PrecioCarrera)

        if id_carrera_ciclo is not None:
            stmt = stmt.where(
                PrecioCarrera.id_carrera_ciclo
                == id_carrera_ciclo
            )

        if id_grado is not None:
            stmt = stmt.where(
                PrecioCarrera.id_grado
                == id_grado
            )

        if tipo is not None:
            stmt = stmt.where(
                PrecioCarrera.tipo == tipo
            )

        if activo is not None:
            stmt = stmt.where(
                PrecioCarrera.activo == activo
            )

        stmt = stmt.order_by(
            PrecioCarrera.id_carrera_ciclo,
            PrecioCarrera.id_grado,
            PrecioCarrera.tipo,
            PrecioCarrera.fecha_inicio.desc(),
        )

        return list(
            db.scalars(stmt).all()
        )

    @staticmethod
    def buscar_solapado(
        db: Session,
        id_carrera_ciclo: int,
        id_grado: int,
        tipo: str,
        concepto: str,
        fecha_inicio: date,
        fecha_fin: date | None,
        excluir_id: int | None = None,
    ) -> PrecioCarrera | None:

        limite_fin = fecha_fin or date.max

        stmt = select(PrecioCarrera).where(
            PrecioCarrera.id_carrera_ciclo
            == id_carrera_ciclo,

            PrecioCarrera.id_grado
            == id_grado,

            PrecioCarrera.tipo == tipo,

            PrecioCarrera.concepto == concepto,

            PrecioCarrera.activo.is_(True),

            PrecioCarrera.fecha_inicio
            <= limite_fin,

            or_(
                PrecioCarrera.fecha_fin.is_(None),
                PrecioCarrera.fecha_fin
                >= fecha_inicio,
            ),
        )

        if excluir_id is not None:
            stmt = stmt.where(
                PrecioCarrera.id_precio
                != excluir_id
            )

        return db.scalar(stmt)