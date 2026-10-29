from sqlalchemy import text
from sqlalchemy.orm import Session


class ReporteRepository:

    @staticmethod
    def dashboard(
        db: Session,
    ) -> dict:

        row = db.execute(
            text(
                """
                SELECT
                    estudiantes_activos,
                    inscripciones_activas,
                    total_pagado,
                    deuda_total,
                    estudiantes_insolventes
                FROM school.vw_dashboard_financiero
                """
            )
        ).mappings().first()

        if row is None:
            return {
                "estudiantes_activos": 0,
                "inscripciones_activas": 0,
                "total_pagado": 0,
                "deuda_total": 0,
                "estudiantes_insolventes": 0,
            }

        return dict(row)

    @staticmethod
    def deuda_por_grado(
        db: Session,
    ) -> list[dict]:

        rows = db.execute(
            text(
                """
                SELECT
                    id_grado,
                    grado,
                    cantidad_estudiantes,
                    deuda_total
                FROM school.vw_deuda_por_grado
                ORDER BY
                    deuda_total DESC,
                    grado
                """
            )
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def deuda_por_estudiante(
        db: Session,
        buscar: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:

        filtros = []
        params = {
            "offset": offset,
            "limit": limit,
        }

        if buscar:
            filtros.append(
                """
                (
                    codigo_estudiante ILIKE :buscar
                    OR estudiante ILIKE :buscar
                    OR grado ILIKE :buscar
                )
                """
            )

            params["buscar"] = (
                f"%{buscar.strip()}%"
            )

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
                    id_estudiante,
                    codigo_estudiante,
                    estudiante,
                    grado,
                    deuda_total

                FROM school.vw_deuda_por_estudiante

                {where_sql}

                ORDER BY
                    deuda_total DESC,
                    estudiante

                OFFSET :offset
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def estudiantes_insolventes(
        db: Session,
        buscar: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:

        filtros = []
        params = {
            "offset": offset,
            "limit": limit,
        }

        if buscar:
            filtros.append(
                """
                (
                    codigo_estudiante ILIKE :buscar
                    OR estudiante ILIKE :buscar
                    OR grado ILIKE :buscar
                )
                """
            )

            params["buscar"] = (
                f"%{buscar.strip()}%"
            )

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
                    id_estudiante,
                    codigo_estudiante,
                    estudiante,
                    id_inscripcion,
                    grado,
                    deuda_total

                FROM school.vw_estudiantes_insolventes

                {where_sql}

                ORDER BY
                    deuda_total DESC,
                    estudiante

                OFFSET :offset
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def estado_cuenta_estudiante(
        db: Session,
        id_estudiante: int,
        id_inscripcion: int | None = None,
    ) -> list[dict]:

        filtros = [
            "id_estudiante = :id_estudiante"
        ]

        params = {
            "id_estudiante": id_estudiante,
        }

        if id_inscripcion is not None:
            filtros.append(
                "id_inscripcion = :id_inscripcion"
            )

            params["id_inscripcion"] = (
                id_inscripcion
            )

        where_sql = (
            "WHERE "
            + " AND ".join(filtros)
        )

        rows = db.execute(
            text(
                f"""
                SELECT
                    id_estudiante,
                    codigo_estudiante,
                    estudiante,

                    id_inscripcion,

                    carrera,
                    grado,

                    id_obligacion,

                    concepto,
                    periodo,
                    fecha_vencimiento,

                    total_pagado,
                    saldo

                FROM school.vw_estado_cuenta_estudiante

                {where_sql}

                ORDER BY
                    fecha_vencimiento NULLS LAST,
                    id_obligacion
                """
            ),
            params,
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]