from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.models.beca import Beca
from app.models.beca_estudiante import (
    BecaEstudiante,
)
from app.models.estudiante import Estudiante


class BecaRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_beca: int,
    ) -> Beca | None:
        return db.get(
            Beca,
            id_beca,
        )

    @staticmethod
    def get_by_nombre(
        db: Session,
        nombre: str,
    ) -> Beca | None:

        stmt = select(Beca).where(
            Beca.nombre == nombre
        )

        return db.scalar(stmt)

    @staticmethod
    def list(
        db: Session,
        estado: str | None = None,
    ) -> list[Beca]:

        stmt = select(Beca)

        if estado is not None:
            stmt = stmt.where(
                Beca.estado == estado
            )

        stmt = stmt.order_by(
            Beca.nombre
        )

        return list(
            db.scalars(stmt).all()
        )

    @staticmethod
    def get_asignacion(
        db: Session,
        id_beca_estudiante: int,
    ) -> BecaEstudiante | None:

        return db.get(
            BecaEstudiante,
            id_beca_estudiante,
        )

    @staticmethod
    def buscar_asignacion_solapada(
        db: Session,
        id_beca: int,
        id_estudiante: int,
        fecha_inicio: date,
        fecha_fin: date | None,
    ) -> BecaEstudiante | None:

        limite_fin = fecha_fin or date.max

        stmt = select(
            BecaEstudiante
        ).where(
            BecaEstudiante.id_beca == id_beca,
            BecaEstudiante.id_estudiante
            == id_estudiante,

            BecaEstudiante.fecha_inicio
            <= limite_fin,

            or_(
                BecaEstudiante.fecha_fin.is_(None),
                BecaEstudiante.fecha_fin
                >= fecha_inicio,
            ),
        )

        return db.scalar(stmt)

    @staticmethod
    def list_asignaciones(
        db: Session,
        id_estudiante: int | None = None,
        id_beca: int | None = None,
    ) -> list[dict]:

        stmt = (
            select(
                BecaEstudiante.id_beca_estudiante,
                BecaEstudiante.id_beca,
                BecaEstudiante.id_estudiante,

                Beca.nombre.label("beca"),

                func.concat(
                    Estudiante.nombres,
                    " ",
                    Estudiante.apellidos,
                ).label("estudiante"),

                Beca.porcentaje.label(
                    "porcentaje_beca"
                ),

                BecaEstudiante.porcentaje_aplicado,

                func.coalesce(
                    BecaEstudiante.porcentaje_aplicado,
                    Beca.porcentaje,
                ).label("porcentaje_efectivo"),

                BecaEstudiante.fecha_inicio,
                BecaEstudiante.fecha_fin,
                BecaEstudiante.observaciones,
            )
            .join(
                Beca,
                Beca.id_beca
                == BecaEstudiante.id_beca,
            )
            .join(
                Estudiante,
                Estudiante.id_estudiante
                == BecaEstudiante.id_estudiante,
            )
        )

        if id_estudiante is not None:
            stmt = stmt.where(
                BecaEstudiante.id_estudiante
                == id_estudiante
            )

        if id_beca is not None:
            stmt = stmt.where(
                BecaEstudiante.id_beca
                == id_beca
            )

        stmt = stmt.order_by(
            BecaEstudiante.fecha_inicio.desc()
        )

        rows = db.execute(
            stmt
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def aplicar_a_obligacion(
        db: Session,
        id_beca_estudiante: int,
        id_obligacion: int,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT
                    school.fn_aplicar_beca_estudiante_obligacion(
                        :id_beca_estudiante,
                        :id_obligacion
                    )
                """
            ),
            {
                "id_beca_estudiante":
                    id_beca_estudiante,

                "id_obligacion":
                    id_obligacion,
            },
        )
    @staticmethod
    def get_aplicacion(
        db: Session,
        id_beca_obligacion: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    bo.id_beca_obligacion,
                    bo.id_beca_estudiante,
                    bo.id_obligacion,

                    b.nombre AS beca,
                    o.concepto,

                    bo.porcentaje_aplicado,
                    bo.monto_aplicado,
                    bo.fecha_aplicacion,

                    o.monto_beca,
                    o.monto_neto,
                    v.saldo

                FROM school.beca_obligacion bo

                JOIN school.beca_estudiante be
                    ON be.id_beca_estudiante =
                    bo.id_beca_estudiante

                JOIN school.beca b
                    ON b.id_beca = be.id_beca

                JOIN school.obligacion o
                    ON o.id_obligacion =
                    bo.id_obligacion

                JOIN school.vw_saldo_obligaciones v
                    ON v.id_obligacion =
                    bo.id_obligacion

                WHERE bo.id_beca_obligacion =
                    :id_beca_obligacion
                """
            ),
            {
                "id_beca_obligacion":
                    id_beca_obligacion,
            },
        ).mappings().first()

        return dict(row) if row else None

        db.execute(
            text(
                """
                SELECT
                    school.fn_aplicar_beca_obligacion(
                        :id_obligacion,
                        :porcentaje
                    )
                """
            ),
            {
                "id_obligacion": id_obligacion,
                "porcentaje": porcentaje,
            },
        )