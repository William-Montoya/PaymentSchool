from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.expediente import Expediente


class ExpedienteRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_expediente: int,
    ) -> Expediente | None:

        return db.get(
            Expediente,
            id_expediente,
        )

    @staticmethod
    def get_by_estudiante(
        db: Session,
        id_estudiante: int,
    ) -> Expediente | None:

        stmt = select(Expediente).where(
            Expediente.id_estudiante
            == id_estudiante
        )

        return db.scalar(stmt)

    @staticmethod
    def get_detalle(
        db: Session,
        id_expediente: int,
    ) -> dict | None:

        expediente = db.execute(
            text(
                """
                SELECT
                    ex.id_expediente,
                    ex.id_estudiante,
                    ex.observaciones,
                    ex.creado_en,
                    ex.actualizado_en,

                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante

                FROM school.expediente ex

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       ex.id_estudiante

                WHERE ex.id_expediente =
                      :id_expediente
                """
            ),
            {
                "id_expediente":
                    id_expediente,
            },
        ).mappings().first()

        if expediente is None:
            return None

        documentos = db.execute(
            text(
                """
                SELECT
                    td.id_tipo_documento,
                    td.nombre,
                    td.obligatorio,

                    COALESCE(
                        de.entregado,
                        false
                    ) AS entregado,

                    de.id_documento,
                    de.nombre_archivo

                FROM school.tipo_documento td

                LEFT JOIN school.documento_expediente de
                    ON de.id_tipo_documento =
                       td.id_tipo_documento
                   AND de.id_expediente =
                       :id_expediente

                WHERE td.activo = true

                ORDER BY
                    td.obligatorio DESC,
                    td.nombre
                """
            ),
            {
                "id_expediente":
                    id_expediente,
            },
        ).mappings().all()

        documentos = [
            dict(row)
            for row in documentos
        ]

        obligatorios = [
            d
            for d in documentos
            if d["obligatorio"]
        ]

        entregados = [
            d
            for d in obligatorios
            if d["entregado"]
        ]

        requeridos = len(obligatorios)
        cantidad_entregados = len(entregados)

        resultado = dict(expediente)

        resultado["documentos_requeridos"] = (
            requeridos
        )

        resultado["documentos_entregados"] = (
            cantidad_entregados
        )

        resultado["documentos_pendientes"] = (
            requeridos
            - cantidad_entregados
        )

        resultado["completo"] = (
            requeridos == cantidad_entregados
        )

        resultado["documentos"] = documentos

        return resultado