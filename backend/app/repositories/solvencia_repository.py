from sqlalchemy import text
from sqlalchemy.orm import Session


class SolvenciaRepository:

    @staticmethod
    def generar(
        db: Session,
        id_estudiante: int,
        id_inscripcion: int,
        id_evaluacion: int,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT school.fn_generar_solvencia(
                    :id_estudiante,
                    :id_inscripcion,
                    :id_evaluacion
                )
                """
            ),
            {
                "id_estudiante": id_estudiante,
                "id_inscripcion": id_inscripcion,
                "id_evaluacion": id_evaluacion,
            },
        )

    @staticmethod
    def get_existente(
        db: Session,
        id_inscripcion: int,
        id_evaluacion: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT *
                FROM school.solvencia
                WHERE id_inscripcion = :id_inscripcion
                  AND id_evaluacion = :id_evaluacion
                ORDER BY id_solvencia DESC
                LIMIT 1
                """
            ),
            {
                "id_inscripcion": id_inscripcion,
                "id_evaluacion": id_evaluacion,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def get_detalle(
        db: Session,
        id_solvencia: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    s.id_solvencia,
                    s.id_estudiante,
                    s.id_inscripcion,
                    s.id_evaluacion,

                    s.fecha_generacion,
                    s.fecha_corte,
                    s.saldo_corte,
                    s.estado::text AS estado,
                    s.codigo_verificacion,
                    s.observaciones,

                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante,

                    ev.nombre AS evaluacion,
                    ce.nombre AS ciclo,

                    c.nombre AS carrera,
                    g.nombre AS grado

                FROM school.solvencia s

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       s.id_estudiante

                JOIN school.inscripcion i
                    ON i.id_inscripcion =
                       s.id_inscripcion

                JOIN school.carrera_ciclo cc
                    ON cc.id_carrera_ciclo =
                       i.id_carrera_ciclo

                JOIN school.carrera c
                    ON c.id_carrera =
                       cc.id_carrera

                JOIN school.ciclo_escolar ce
                    ON ce.id_ciclo =
                       cc.id_ciclo

                JOIN school.grado g
                    ON g.id_grado =
                       i.id_grado

                JOIN school.evaluacion ev
                    ON ev.id_evaluacion =
                       s.id_evaluacion

                WHERE s.id_solvencia =
                      :id_solvencia
                """
            ),
            {
                "id_solvencia": id_solvencia,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def get_by_codigo(
        db: Session,
        codigo: str,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT id_solvencia
                FROM school.solvencia
                WHERE codigo_verificacion = :codigo
                """
            ),
            {
                "codigo": codigo,
            },
        ).mappings().first()

        if row is None:
            return None

        return SolvenciaRepository.get_detalle(
            db,
            row["id_solvencia"],
        )

    @staticmethod
    def list(
        db: Session,
        id_estudiante: int | None = None,
        id_evaluacion: int | None = None,
        estado: str | None = None,
    ) -> list[dict]:

        filtros = []
        params = {}

        if id_estudiante is not None:
            filtros.append(
                "s.id_estudiante = :id_estudiante"
            )
            params["id_estudiante"] = id_estudiante

        if id_evaluacion is not None:
            filtros.append(
                "s.id_evaluacion = :id_evaluacion"
            )
            params["id_evaluacion"] = id_evaluacion

        if estado is not None:
            filtros.append(
                "s.estado::text = :estado"
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
                    s.id_solvencia,
                    s.id_estudiante,
                    s.id_inscripcion,
                    s.id_evaluacion,

                    s.fecha_generacion,
                    s.fecha_corte,
                    s.saldo_corte,
                    s.estado::text AS estado,
                    s.codigo_verificacion,
                    s.observaciones,

                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante,

                    ev.nombre AS evaluacion,
                    ce.nombre AS ciclo,

                    c.nombre AS carrera,
                    g.nombre AS grado

                FROM school.solvencia s

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       s.id_estudiante

                JOIN school.inscripcion i
                    ON i.id_inscripcion =
                       s.id_inscripcion

                JOIN school.carrera_ciclo cc
                    ON cc.id_carrera_ciclo =
                       i.id_carrera_ciclo

                JOIN school.carrera c
                    ON c.id_carrera =
                       cc.id_carrera

                JOIN school.ciclo_escolar ce
                    ON ce.id_ciclo =
                       cc.id_ciclo

                JOIN school.grado g
                    ON g.id_grado =
                       i.id_grado

                JOIN school.evaluacion ev
                    ON ev.id_evaluacion =
                       s.id_evaluacion

                {where_sql}

                ORDER BY
                    s.fecha_generacion DESC,
                    s.id_solvencia DESC
                """
            ),
            params,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]