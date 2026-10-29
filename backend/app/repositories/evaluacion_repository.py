from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ciclo_escolar import CicloEscolar
from app.models.evaluacion import Evaluacion
from app.models.solvencia import Solvencia


class EvaluacionRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_evaluacion: int,
    ) -> Evaluacion | None:
        return db.get(
            Evaluacion,
            id_evaluacion,
        )

    @staticmethod
    def get_by_nombre_ciclo(
        db: Session,
        id_ciclo: int,
        nombre: str,
    ) -> Evaluacion | None:

        stmt = select(Evaluacion).where(
            Evaluacion.id_ciclo == id_ciclo,
            Evaluacion.nombre == nombre,
        )

        return db.scalar(stmt)

    @staticmethod
    def list(
        db: Session,
        id_ciclo: int | None = None,
        activo: bool | None = None,
    ) -> list[Evaluacion]:

        stmt = select(Evaluacion)

        if id_ciclo is not None:
            stmt = stmt.where(
                Evaluacion.id_ciclo == id_ciclo
            )

        if activo is not None:
            stmt = stmt.where(
                Evaluacion.activo == activo
            )

        stmt = stmt.order_by(
            Evaluacion.fecha_evaluacion.desc(),
            Evaluacion.id_evaluacion.desc(),
        )

        return list(
            db.scalars(stmt).all()
        )

    @staticmethod
    def list_detalle(
        db: Session,
        id_ciclo: int | None = None,
        activo: bool | None = None,
    ) -> list[dict]:

        stmt = (
            select(
                Evaluacion.id_evaluacion,
                Evaluacion.id_ciclo,
                Evaluacion.nombre,
                Evaluacion.fecha_evaluacion,
                Evaluacion.fecha_corte_finanzas,
                Evaluacion.activo,
                CicloEscolar.nombre.label("ciclo"),
            )
            .join(
                CicloEscolar,
                CicloEscolar.id_ciclo
                == Evaluacion.id_ciclo,
            )
        )

        if id_ciclo is not None:
            stmt = stmt.where(
                Evaluacion.id_ciclo == id_ciclo
            )

        if activo is not None:
            stmt = stmt.where(
                Evaluacion.activo == activo
            )

        stmt = stmt.order_by(
            Evaluacion.fecha_evaluacion.desc()
        )

        rows = db.execute(
            stmt
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def tiene_solvencias(
        db: Session,
        id_evaluacion: int,
    ) -> bool:

        stmt = (
            select(Solvencia.id_solvencia)
            .where(
                Solvencia.id_evaluacion
                == id_evaluacion
            )
            .limit(1)
        )

        return db.scalar(stmt) is not None