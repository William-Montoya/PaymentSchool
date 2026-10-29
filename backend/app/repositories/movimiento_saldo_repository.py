from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session


class MovimientoSaldoRepository:

    @staticmethod
    def trasladar(
        db: Session,
        id_estudiante: int,
        id_inscripcion_origen: int,
        id_inscripcion_destino: int,
        monto: Decimal,
        motivo: str,
        id_usuario: int | None = None,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT school.fn_trasladar_saldo(
                    :id_estudiante,
                    :id_inscripcion_origen,
                    :id_inscripcion_destino,
                    :monto,
                    :motivo,
                    :id_usuario
                )
                """
            ),
            {
                "id_estudiante":
                    id_estudiante,
                "id_inscripcion_origen":
                    id_inscripcion_origen,
                "id_inscripcion_destino":
                    id_inscripcion_destino,
                "monto": monto,
                "motivo": motivo,
                "id_usuario": id_usuario,
            },
        )

    @staticmethod
    def actualizar_referencia(
        db: Session,
        id_movimiento: int,
        referencia: str | None,
    ) -> None:

        db.execute(
            text(
                """
                UPDATE school.movimiento_saldo
                SET referencia = :referencia
                WHERE id_movimiento = :id_movimiento
                """
            ),
            {
                "id_movimiento": id_movimiento,
                "referencia": referencia,
            },
        )

    @staticmethod
    def get_by_id(
        db: Session,
        id_movimiento: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    ms.id_movimiento,

                    ms.id_estudiante,

                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante,

                    ms.id_inscripcion_origen,
                    ms.id_inscripcion_destino,

                    co.nombre AS carrera_origen,
                    cd.nombre AS carrera_destino,

                    go.nombre AS grado_origen,
                    gd.nombre AS grado_destino,

                    ms.tipo::text AS tipo,
                    ms.monto,
                    ms.fecha_movimiento,
                    ms.motivo,
                    ms.estado::text AS estado,
                    ms.id_usuario,
                    ms.referencia

                FROM school.movimiento_saldo ms

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       ms.id_estudiante

                LEFT JOIN school.inscripcion io
                    ON io.id_inscripcion =
                       ms.id_inscripcion_origen

                LEFT JOIN school.carrera_ciclo cco
                    ON cco.id_carrera_ciclo =
                       io.id_carrera_ciclo

                LEFT JOIN school.carrera co
                    ON co.id_carrera =
                       cco.id_carrera

                LEFT JOIN school.grado go
                    ON go.id_grado =
                       io.id_grado

                LEFT JOIN school.inscripcion idest
                    ON idest.id_inscripcion =
                       ms.id_inscripcion_destino

                LEFT JOIN school.carrera_ciclo ccd
                    ON ccd.id_carrera_ciclo =
                       idest.id_carrera_ciclo

                LEFT JOIN school.carrera cd
                    ON cd.id_carrera =
                       ccd.id_carrera

                LEFT JOIN school.grado gd
                    ON gd.id_grado =
                       idest.id_grado

                WHERE ms.id_movimiento =
                      :id_movimiento
                """
            ),
            {
                "id_movimiento": id_movimiento,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def list(
        db: Session,
        id_estudiante: int | None = None,
        tipo: str | None = None,
        estado: str | None = None,
    ) -> list[dict]:

        filtros = []
        params = {}

        if id_estudiante is not None:
            filtros.append(
                "ms.id_estudiante = :id_estudiante"
            )
            params["id_estudiante"] = id_estudiante

        if tipo is not None:
            filtros.append(
                "ms.tipo::text = :tipo"
            )
            params["tipo"] = tipo

        if estado is not None:
            filtros.append(
                "ms.estado::text = :estado"
            )
            params["estado"] = estado

        where_sql = ""

        if filtros:
            where_sql = (
                "WHERE "
                + " AND ".join(filtros)
            )

        ids = db.execute(
            text(
                f"""
                SELECT ms.id_movimiento
                FROM school.movimiento_saldo ms

                {where_sql}

                ORDER BY
                    ms.fecha_movimiento DESC,
                    ms.id_movimiento DESC
                """
            ),
            params,
        ).scalars().all()

        resultado = []

        for id_movimiento in ids:
            item = (
                MovimientoSaldoRepository
                .get_by_id(
                    db,
                    id_movimiento,
                )
            )

            if item is not None:
                resultado.append(item)

        return resultado