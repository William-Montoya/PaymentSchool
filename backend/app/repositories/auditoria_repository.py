import json
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class AuditoriaRepository:

    @staticmethod
    def registrar(
        db: Session,
        id_usuario: int | None,
        modulo: str,
        accion: str,
        tabla_afectada: str | None,
        id_registro: int | None,
        descripcion: str | None,
        datos_anteriores: Any | None = None,
        datos_nuevos: Any | None = None,
    ) -> None:

        datos_anteriores_json = (
            json.dumps(
                datos_anteriores,
                ensure_ascii=False,
            )
            if datos_anteriores is not None
            else None
        )

        datos_nuevos_json = (
            json.dumps(
                datos_nuevos,
                ensure_ascii=False,
            )
            if datos_nuevos is not None
            else None
        )

        db.execute(
            text(
                """
                SELECT school.fn_registrar_auditoria(
                    CAST(:id_usuario AS bigint),
                    CAST(:modulo AS varchar),
                    CAST(:accion AS varchar),
                    CAST(:tabla_afectada AS varchar),
                    CAST(:id_registro AS bigint),
                    CAST(:descripcion AS text),
                    CAST(:datos_anteriores AS jsonb),
                    CAST(:datos_nuevos AS jsonb)
                )
                """
            ),
            {
                "id_usuario": id_usuario,
                "modulo": modulo,
                "accion": accion,
                "tabla_afectada": tabla_afectada,
                "id_registro": id_registro,
                "descripcion": descripcion,
                "datos_anteriores": datos_anteriores_json,
                "datos_nuevos": datos_nuevos_json,
            },
        )

    @staticmethod
    def get_by_id(
        db: Session,
        id_auditoria: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    a.id_auditoria,
                    a.id_usuario,
                    u.username,
                    a.fecha_evento,
                    a.modulo,
                    a.accion,
                    a.tabla_afectada,
                    a.id_registro,
                    a.descripcion,
                    a.datos_anteriores,
                    a.datos_nuevos,
                    a.ip

                FROM school.auditoria a

                LEFT JOIN school.usuario u
                    ON u.id_usuario =
                       a.id_usuario

                WHERE a.id_auditoria =
                      :id_auditoria
                """
            ),
            {
                "id_auditoria": id_auditoria,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def list(
        db: Session,
        id_usuario: int | None = None,
        modulo: str | None = None,
        accion: str | None = None,
        tabla_afectada: str | None = None,
        id_registro: int | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:

        filtros = []

        params = {
            "offset": offset,
            "limit": limit,
        }

        if id_usuario is not None:
            filtros.append(
                "a.id_usuario = :id_usuario"
            )
            params["id_usuario"] = id_usuario

        if modulo is not None:
            filtros.append(
                "UPPER(a.modulo) = UPPER(:modulo)"
            )
            params["modulo"] = modulo

        if accion is not None:
            filtros.append(
                "UPPER(a.accion) = UPPER(:accion)"
            )
            params["accion"] = accion

        if tabla_afectada is not None:
            filtros.append(
                """
                LOWER(a.tabla_afectada) =
                LOWER(:tabla_afectada)
                """
            )

            params["tabla_afectada"] = (
                tabla_afectada
            )

        if id_registro is not None:
            filtros.append(
                "a.id_registro = :id_registro"
            )
            params["id_registro"] = id_registro

        if fecha_desde is not None:
            filtros.append(
                "a.fecha_evento >= :fecha_desde"
            )
            params["fecha_desde"] = fecha_desde

        if fecha_hasta is not None:
            filtros.append(
                "a.fecha_evento <= :fecha_hasta"
            )
            params["fecha_hasta"] = fecha_hasta

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
                    a.id_auditoria,
                    a.id_usuario,
                    u.username,
                    a.fecha_evento,
                    a.modulo,
                    a.accion,
                    a.tabla_afectada,
                    a.id_registro,
                    a.descripcion,
                    a.datos_anteriores,
                    a.datos_nuevos,
                    a.ip

                FROM school.auditoria a

                LEFT JOIN school.usuario u
                    ON u.id_usuario =
                       a.id_usuario

                {where_sql}

                ORDER BY
                    a.fecha_evento DESC,
                    a.id_auditoria DESC

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
    def catalogos(
        db: Session,
    ) -> dict:

        usuarios = db.execute(
            text(
                """
                SELECT DISTINCT
                    u.id_usuario,
                    u.username
                FROM school.auditoria a
                JOIN school.usuario u
                    ON u.id_usuario = a.id_usuario
                ORDER BY u.username
                """
            )
        ).mappings().all()

        modulos = db.execute(
            text(
                """
                SELECT DISTINCT modulo
                FROM school.auditoria
                WHERE modulo IS NOT NULL
                  AND BTRIM(modulo) <> ''
                ORDER BY modulo
                """
            )
        ).scalars().all()

        acciones = db.execute(
            text(
                """
                SELECT DISTINCT accion
                FROM school.auditoria
                WHERE accion IS NOT NULL
                  AND BTRIM(accion) <> ''
                ORDER BY accion
                """
            )
        ).scalars().all()

        tablas = db.execute(
            text(
                """
                SELECT DISTINCT tabla_afectada
                FROM school.auditoria
                WHERE tabla_afectada IS NOT NULL
                  AND BTRIM(tabla_afectada) <> ''
                ORDER BY tabla_afectada
                """
            )
        ).scalars().all()

        return {
            "usuarios": [
                dict(row)
                for row in usuarios
            ],
            "modulos": list(modulos),
            "acciones": list(acciones),
            "tablas": list(tablas),
        }
