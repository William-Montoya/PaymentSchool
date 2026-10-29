from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session


class SaldoFavorRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_saldo_favor: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    id_saldo_favor,
                    id_estudiante,
                    id_pago_origen,
                    monto_original,
                    monto_disponible,
                    fecha_generacion,
                    estado,
                    observaciones

                FROM school.saldo_favor

                WHERE id_saldo_favor =
                      :id_saldo_favor
                """
            ),
            {
                "id_saldo_favor": id_saldo_favor,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def get_activo_by_pago(
        db: Session,
        id_pago: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    id_saldo_favor,
                    id_estudiante,
                    id_pago_origen,
                    monto_original,
                    monto_disponible,
                    fecha_generacion,
                    estado,
                    observaciones

                FROM school.saldo_favor

                WHERE id_pago_origen = :id_pago
                  AND estado = 'ACTIVO'
                  AND monto_disponible > 0

                ORDER BY id_saldo_favor DESC

                LIMIT 1
                """
            ),
            {
                "id_pago": id_pago,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def list(
        db: Session,
        id_estudiante: int | None = None,
        estado: str | None = None,
    ) -> list[dict]:

        filtros = []
        params = {}

        if id_estudiante is not None:
            filtros.append(
                "id_estudiante = :id_estudiante"
            )
            params["id_estudiante"] = id_estudiante

        if estado is not None:
            filtros.append(
                "estado = :estado"
            )
            params["estado"] = estado

        where_sql = ""

        if filtros:
            where_sql = (
                "WHERE "
                + " AND ".join(filtros)
            )

        rows = db.execute(
            text(
                f"""
                SELECT
                    id_saldo_favor,
                    id_estudiante,
                    id_pago_origen,
                    monto_original,
                    monto_disponible,
                    fecha_generacion,
                    estado,
                    observaciones

                FROM school.saldo_favor

                {where_sql}

                ORDER BY
                    fecha_generacion DESC,
                    id_saldo_favor DESC
                """
            ),
            params,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def aplicar(
        db: Session,
        id_saldo_favor: int,
        id_obligacion: int,
        monto: Decimal,
    ) -> None:

        db.execute(
            text(
                """
                SELECT school.fn_aplicar_saldo_favor(
                    :id_saldo_favor,
                    :id_obligacion,
                    :monto
                )
                """
            ),
            {
                "id_saldo_favor": id_saldo_favor,
                "id_obligacion": id_obligacion,
                "monto": monto,
            },
        )