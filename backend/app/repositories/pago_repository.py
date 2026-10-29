from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.obligacion import Obligacion


class PagoRepository:

    @staticmethod
    def bloquear_obligaciones(
        db: Session,
        ids_obligaciones: list[int],
    ) -> list[int]:

        if not ids_obligaciones:
            return []

        stmt = (
            select(
                Obligacion.id_obligacion
            )
            .where(
                Obligacion.id_obligacion.in_(
                    ids_obligaciones
                )
            )
            .order_by(
                Obligacion.id_obligacion
            )
            .with_for_update()
        )

        return list(
            db.scalars(stmt).all()
        )

    @staticmethod
    def get_obligaciones_cobro(
        db: Session,
        ids_obligaciones: list[int],
    ) -> list[dict]:

        if not ids_obligaciones:
            return []

        placeholders = []

        params = {}

        for index, id_obligacion in enumerate(
            ids_obligaciones
        ):
            key = (
                f"id_obligacion_{index}"
            )

            placeholders.append(
                f":{key}"
            )

            params[key] = id_obligacion

        ids_sql = ", ".join(
            placeholders
        )

        rows = db.execute(
            text(
                f"""
                SELECT
                    o.id_obligacion,
                    o.id_inscripcion,

                    i.id_estudiante,

                    o.concepto,
                    o.periodo,
                    o.fecha_vencimiento,

                    o.monto_neto,

                    o.estado::text
                        AS estado,

                    o.tipo_obligacion,

                    v.total_pagado,
                    v.saldo

                FROM school.obligacion o

                JOIN school.inscripcion i
                    ON i.id_inscripcion =
                       o.id_inscripcion

                JOIN school.vw_saldo_obligaciones v
                    ON v.id_obligacion =
                       o.id_obligacion

                WHERE o.id_obligacion IN (
                    {ids_sql}
                )

                ORDER BY
                    o.fecha_vencimiento
                        NULLS LAST,
                    o.periodo
                        NULLS LAST,
                    o.id_obligacion
                """
            ),
            params,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def list_mensualidades_abiertas(
        db: Session,
        id_inscripcion: int,
    ) -> list[dict]:

        rows = db.execute(
            text(
                """
                SELECT
                    o.id_obligacion,
                    o.id_inscripcion,

                    o.concepto,
                    o.periodo,
                    o.fecha_vencimiento,

                    o.estado::text
                        AS estado,

                    v.saldo

                FROM school.obligacion o

                JOIN school.vw_saldo_obligaciones v
                    ON v.id_obligacion =
                       o.id_obligacion

                WHERE
                    o.id_inscripcion =
                        :id_inscripcion

                    AND o.tipo_obligacion =
                        'MENSUALIDAD'

                    AND o.estado IN (
                        'PENDIENTE',
                        'PARCIAL'
                    )

                    AND v.saldo > 0

                ORDER BY
                    o.periodo
                        NULLS LAST,
                    o.fecha_vencimiento
                        NULLS LAST,
                    o.id_obligacion
                """
            ),
            {
                "id_inscripcion":
                    id_inscripcion,
            },
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def registrar(
        db: Session,
        id_estudiante: int,
        monto: Decimal,
        metodo: str,
        referencia: str | None,
        observaciones: str | None,
        id_usuario: int | None = None,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT school.fn_registrar_pago(
                    :id_estudiante,
                    :monto,
                    CAST(
                        :metodo
                        AS school.metodo_pago
                    ),
                    CAST(
                        :referencia
                        AS varchar
                    ),
                    CAST(
                        :observaciones
                        AS text
                    ),
                    CAST(
                        :id_usuario
                        AS bigint
                    )
                )
                """
            ),
            {
                "id_estudiante":
                    id_estudiante,
                "monto":
                    monto,
                "metodo":
                    metodo,
                "referencia":
                    referencia,
                "observaciones":
                    observaciones,
                "id_usuario":
                    id_usuario,
            },
        )

    @staticmethod
    def registrar_automatico(
        db: Session,
        id_estudiante: int,
        monto: Decimal,
        metodo: str,
        referencia: str | None,
        observaciones: str | None,
        id_usuario: int | None = None,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT
                    school
                    .fn_registrar_pago_automatico(
                        :id_estudiante,
                        :monto,
                        CAST(
                            :metodo
                            AS school.metodo_pago
                        ),
                        CAST(
                            :referencia
                            AS varchar
                        ),
                        CAST(
                            :observaciones
                            AS text
                        ),
                        CAST(
                            :id_usuario
                            AS bigint
                        )
                    )
                """
            ),
            {
                "id_estudiante":
                    id_estudiante,
                "monto":
                    monto,
                "metodo":
                    metodo,
                "referencia":
                    referencia,
                "observaciones":
                    observaciones,
                "id_usuario":
                    id_usuario,
            },
        )

    @staticmethod
    def aplicar(
        db: Session,
        id_pago: int,
        id_obligacion: int,
        monto: Decimal,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT school.fn_aplicar_pago(
                    :id_pago,
                    :id_obligacion,
                    :monto
                )
                """
            ),
            {
                "id_pago":
                    id_pago,
                "id_obligacion":
                    id_obligacion,
                "monto":
                    monto,
            },
        )

    @staticmethod
    def anular(
        db: Session,
        id_pago: int,
        motivo: str,
        id_usuario: int | None = None,
    ) -> None:

        db.execute(
            text(
                """
                SELECT school.fn_anular_pago(
                    :id_pago,
                    CAST(
                        :motivo
                        AS text
                    ),
                    CAST(
                        :id_usuario
                        AS bigint
                    )
                )
                """
            ),
            {
                "id_pago":
                    id_pago,
                "motivo":
                    motivo,
                "id_usuario":
                    id_usuario,
            },
        )

    @staticmethod
    def get_by_id(
        db: Session,
        id_pago: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    p.id_pago,
                    p.id_estudiante,
                    p.id_usuario,
                    p.fecha_pago,
                    p.monto_total,
                    p.metodo::text
                        AS metodo,
                    p.referencia,
                    p.observaciones,
                    p.estado::text
                        AS estado,
                    p.creado_en,

                    COALESCE(
                        (
                            SELECT
                                SUM(
                                    ap.monto_aplicado
                                )

                            FROM
                                school
                                .aplicacion_pago ap

                            WHERE
                                ap.id_pago =
                                    p.id_pago
                        ),
                        0
                    ) AS total_aplicado,

                    school
                    .fn_saldo_disponible_pago(
                        p.id_pago
                    )
                        AS saldo_disponible

                FROM school.pago p

                WHERE
                    p.id_pago =
                        :id_pago
                """
            ),
            {
                "id_pago":
                    id_pago,
            },
        ).mappings().first()

        return (
            dict(row)
            if row
            else None
        )

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
                (
                    "p.id_estudiante = "
                    ":id_estudiante"
                )
            )

            params[
                "id_estudiante"
            ] = id_estudiante

        if estado is not None:
            filtros.append(
                (
                    "p.estado::text = "
                    ":estado"
                )
            )

            params[
                "estado"
            ] = estado

        where_sql = ""

        if filtros:
            where_sql = (
                "WHERE "
                + " AND ".join(
                    filtros
                )
            )

        rows = db.execute(
            text(
                f"""
                SELECT
                    p.id_pago,
                    p.id_estudiante,
                    p.id_usuario,
                    p.fecha_pago,
                    p.monto_total,
                    p.metodo::text
                        AS metodo,
                    p.referencia,
                    p.observaciones,
                    p.estado::text
                        AS estado,
                    p.creado_en,

                    COALESCE(
                        (
                            SELECT
                                SUM(
                                    ap.monto_aplicado
                                )

                            FROM
                                school
                                .aplicacion_pago ap

                            WHERE
                                ap.id_pago =
                                    p.id_pago
                        ),
                        0
                    ) AS total_aplicado,

                    school
                    .fn_saldo_disponible_pago(
                        p.id_pago
                    )
                        AS saldo_disponible

                FROM school.pago p

                {where_sql}

                ORDER BY
                    p.fecha_pago DESC,
                    p.id_pago DESC
                """
            ),
            params,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def get_aplicacion(
        db: Session,
        id_aplicacion: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    ap.id_aplicacion,
                    ap.id_pago,
                    ap.id_obligacion,

                    o.concepto,
                    o.periodo,

                    ap.monto_aplicado,
                    ap.fecha_aplicacion

                FROM
                    school
                    .aplicacion_pago ap

                JOIN school.obligacion o
                    ON o.id_obligacion =
                       ap.id_obligacion

                WHERE
                    ap.id_aplicacion =
                        :id_aplicacion
                """
            ),
            {
                "id_aplicacion":
                    id_aplicacion,
            },
        ).mappings().first()

        return (
            dict(row)
            if row
            else None
        )

    @staticmethod
    def list_aplicaciones(
        db: Session,
        id_pago: int,
    ) -> list[dict]:

        rows = db.execute(
            text(
                """
                SELECT
                    ap.id_aplicacion,
                    ap.id_pago,
                    ap.id_obligacion,

                    o.concepto,
                    o.periodo,

                    ap.monto_aplicado,
                    ap.fecha_aplicacion

                FROM
                    school
                    .aplicacion_pago ap

                JOIN school.obligacion o
                    ON o.id_obligacion =
                       ap.id_obligacion

                WHERE
                    ap.id_pago =
                        :id_pago

                ORDER BY
                    ap.fecha_aplicacion,
                    ap.id_aplicacion
                """
            ),
            {
                "id_pago":
                    id_pago,
            },
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def list_aplicaciones_detalle(
        db: Session,
        id_pago: int,
    ) -> list[dict]:

        rows = db.execute(
            text(
                """
                SELECT
                    ap.id_aplicacion,
                    ap.id_pago,
                    ap.id_obligacion,

                    o.concepto,
                    o.periodo,

                    o.tipo_obligacion,

                    o.fecha_vencimiento,

                    o.monto_neto
                        AS monto_obligacion,

                    ap.monto_aplicado,

                    ap.fecha_aplicacion

                FROM
                    school
                    .aplicacion_pago ap

                JOIN school.obligacion o
                    ON o.id_obligacion =
                       ap.id_obligacion

                WHERE
                    ap.id_pago =
                        :id_pago

                ORDER BY
                    o.fecha_vencimiento
                        NULLS LAST,
                    o.periodo
                        NULLS LAST,
                    ap.id_aplicacion
                """
            ),
            {
                "id_pago":
                    id_pago,
            },
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]