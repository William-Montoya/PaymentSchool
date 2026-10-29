from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.obligacion import Obligacion


class ObligacionRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_obligacion: int,
    ) -> Obligacion | None:
        return db.get(
            Obligacion,
            id_obligacion,
        )

    @staticmethod
    def existe_desde_precio(
        db: Session,
        id_inscripcion: int,
        id_precio: int,
    ) -> bool:

        stmt = (
            select(Obligacion.id_obligacion)
            .where(
                Obligacion.id_inscripcion
                == id_inscripcion,
                Obligacion.id_precio
                == id_precio,
                Obligacion.estado != "ANULADA",
            )
            .limit(1)
        )

        return db.scalar(stmt) is not None

    @staticmethod
    def create(
        db: Session,
        obligacion: Obligacion,
    ) -> Obligacion:

        db.add(obligacion)
        db.flush()
        db.refresh(obligacion)

        return obligacion

    @staticmethod
    def generar_mensualidades(
        db: Session,
        id_inscripcion: int,
        id_precio: int,
        fecha_inicio,
        cantidad_meses: int,
    ) -> None:

        db.execute(
            text(
                """
                SELECT school.fn_generar_obligaciones_mensuales(
                    :id_inscripcion,
                    :id_precio,
                    :fecha_inicio,
                    :cantidad_meses
                )
                """
            ),
            {
                "id_inscripcion": id_inscripcion,
                "id_precio": id_precio,
                "fecha_inicio": fecha_inicio,
                "cantidad_meses": cantidad_meses,
            },
        )

    @staticmethod
    def get_con_saldo(
        db: Session,
        id_obligacion: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    o.id_obligacion,
                    o.id_inscripcion,
                    o.id_precio,
                    o.concepto,
                    o.periodo,
                    o.fecha_vencimiento,
                    o.monto_bruto,
                    o.monto_descuento,
                    o.monto_beca,
                    o.monto_neto,
                    o.estado::text AS estado,
                    o.tipo_obligacion,
                    o.creado_en,
                    v.total_pagado,
                    v.saldo
                FROM school.obligacion o
                JOIN school.vw_saldo_obligaciones v
                    ON v.id_obligacion = o.id_obligacion
                WHERE o.id_obligacion = :id_obligacion
                """
            ),
            {
                "id_obligacion": id_obligacion,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def list_con_saldo(
        db: Session,
        id_inscripcion: int | None = None,
        estado: str | None = None,
        tipo_obligacion: str | None = None,
    ) -> list[dict]:

        filtros = []
        parametros = {}

        if id_inscripcion is not None:
            filtros.append(
                "o.id_inscripcion = :id_inscripcion"
            )
            parametros["id_inscripcion"] = id_inscripcion

        if estado is not None:
            filtros.append(
                "o.estado::text = :estado"
            )
            parametros["estado"] = estado

        if tipo_obligacion is not None:
            filtros.append(
                "o.tipo_obligacion = :tipo_obligacion"
            )
            parametros["tipo_obligacion"] = tipo_obligacion

        where_sql = ""

        if filtros:
            where_sql = (
                "WHERE "
                + " AND ".join(filtros)
            )

        sql = text(
            f"""
            SELECT
                o.id_obligacion,
                o.id_inscripcion,
                o.id_precio,
                o.concepto,
                o.periodo,
                o.fecha_vencimiento,
                o.monto_bruto,
                o.monto_descuento,
                o.monto_beca,
                o.monto_neto,
                o.estado::text AS estado,
                o.tipo_obligacion,
                o.creado_en,
                v.total_pagado,
                v.saldo
            FROM school.obligacion o
            JOIN school.vw_saldo_obligaciones v
                ON v.id_obligacion = o.id_obligacion
            {where_sql}
            ORDER BY
                o.fecha_vencimiento NULLS LAST,
                o.id_obligacion
            """
        )

        rows = db.execute(
            sql,
            parametros,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]