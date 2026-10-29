from sqlalchemy import text
from sqlalchemy.orm import Session


class CambioCarreraRepository:

    @staticmethod
    def ejecutar(
        db: Session,
        id_estudiante: int,
        id_inscripcion_origen: int,
        id_carrera_ciclo_destino: int,
        id_grado_destino: int,
        motivo: str,
        id_usuario: int | None = None,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT school.fn_cambiar_carrera(
                    :id_estudiante,
                    :id_inscripcion_origen,
                    :id_carrera_ciclo_destino,
                    :id_grado_destino,
                    :motivo,
                    :id_usuario
                )
                """
            ),
            {
                "id_estudiante": id_estudiante,
                "id_inscripcion_origen":
                    id_inscripcion_origen,
                "id_carrera_ciclo_destino":
                    id_carrera_ciclo_destino,
                "id_grado_destino":
                    id_grado_destino,
                "motivo": motivo,
                "id_usuario": id_usuario,
            },
        )

    @staticmethod
    def actualizar_observaciones(
        db: Session,
        id_cambio: int,
        observaciones: str | None,
    ) -> None:

        db.execute(
            text(
                """
                UPDATE school.cambio_carrera
                SET observaciones = :observaciones
                WHERE id_cambio = :id_cambio
                """
            ),
            {
                "id_cambio": id_cambio,
                "observaciones": observaciones,
            },
        )

    @staticmethod
    def get_by_id(
        db: Session,
        id_cambio: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    cc.id_cambio,

                    cc.id_estudiante,
                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante,

                    cc.id_inscripcion_origen,
                    cc.id_inscripcion_destino,

                    io.id_carrera_ciclo
                        AS id_carrera_ciclo_origen,

                    idest.id_carrera_ciclo
                        AS id_carrera_ciclo_destino,

                    co.nombre AS carrera_origen,
                    cd.nombre AS carrera_destino,

                    go.nombre AS grado_origen,
                    gd.nombre AS grado_destino,

                    ciclo.nombre AS ciclo,

                    io.estado::text
                        AS estado_inscripcion_origen,

                    idest.estado::text
                        AS estado_inscripcion_destino,

                    cc.fecha_solicitud,
                    cc.fecha_aprobacion,
                    cc.motivo,
                    cc.estado::text AS estado,
                    cc.id_usuario,
                    cc.observaciones

                FROM school.cambio_carrera cc

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       cc.id_estudiante

                JOIN school.inscripcion io
                    ON io.id_inscripcion =
                       cc.id_inscripcion_origen

                JOIN school.carrera_ciclo cco
                    ON cco.id_carrera_ciclo =
                       io.id_carrera_ciclo

                JOIN school.carrera co
                    ON co.id_carrera =
                       cco.id_carrera

                JOIN school.grado go
                    ON go.id_grado =
                       io.id_grado

                JOIN school.ciclo_escolar ciclo
                    ON ciclo.id_ciclo =
                       cco.id_ciclo

                LEFT JOIN school.inscripcion idest
                    ON idest.id_inscripcion =
                       cc.id_inscripcion_destino

                LEFT JOIN school.carrera_ciclo ccd
                    ON ccd.id_carrera_ciclo =
                       idest.id_carrera_ciclo

                LEFT JOIN school.carrera cd
                    ON cd.id_carrera =
                       ccd.id_carrera

                LEFT JOIN school.grado gd
                    ON gd.id_grado =
                       idest.id_grado

                WHERE cc.id_cambio = :id_cambio
                """
            ),
            {
                "id_cambio": id_cambio,
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
                "cc.id_estudiante = :id_estudiante"
            )
            params["id_estudiante"] = id_estudiante

        if estado is not None:
            filtros.append(
                "cc.estado::text = :estado"
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
                SELECT cc.id_cambio
                FROM school.cambio_carrera cc
                {where_sql}
                ORDER BY
                    cc.fecha_solicitud DESC,
                    cc.id_cambio DESC
                """
            ),
            params,
        ).scalars().all()

        resultado = []

        for id_cambio in ids:
            item = (
                CambioCarreraRepository
                .get_by_id(
                    db,
                    id_cambio,
                )
            )

            if item is not None:
                resultado.append(item)

        return resultado

    @staticmethod
    def existe_cambio_aprobado(
        db: Session,
        id_estudiante: int,
        id_inscripcion_origen: int,
        id_inscripcion_destino: int,
    ) -> bool:

        resultado = db.scalar(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM school.cambio_carrera
                    WHERE id_estudiante =
                          :id_estudiante
                      AND id_inscripcion_origen =
                          :id_inscripcion_origen
                      AND id_inscripcion_destino =
                          :id_inscripcion_destino
                      AND estado = 'APROBADO'
                )
                """
            ),
            {
                "id_estudiante": id_estudiante,
                "id_inscripcion_origen":
                    id_inscripcion_origen,
                "id_inscripcion_destino":
                    id_inscripcion_destino,
            },
        )

        return bool(resultado)