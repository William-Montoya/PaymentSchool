from sqlalchemy import text
from sqlalchemy.orm import Session


class NotificacionRepository:

    @staticmethod
    def crear(
        db: Session,
        titulo: str,
        mensaje: str,
        id_usuario: int | None = None,
    ) -> int:

        return db.scalar(
            text(
                """
                INSERT INTO school.notificacion (
                    titulo,
                    mensaje,
                    id_usuario
                )
                VALUES (
                    :titulo,
                    :mensaje,
                    :id_usuario
                )
                RETURNING id_notificacion
                """
            ),
            {
                "titulo": titulo,
                "mensaje": mensaje,
                "id_usuario": id_usuario,
            },
        )

    @staticmethod
    def agregar_destinatario(
        db: Session,
        id_notificacion: int,
        id_contacto: int,
    ) -> int:

        return db.scalar(
            text(
                """
                INSERT INTO
                    school.notificacion_destinatario (
                        id_notificacion,
                        id_contacto
                    )
                VALUES (
                    :id_notificacion,
                    :id_contacto
                )
                RETURNING id_destinatario
                """
            ),
            {
                "id_notificacion":
                    id_notificacion,
                "id_contacto":
                    id_contacto,
            },
        )

    @staticmethod
    def get_by_id(
        db: Session,
        id_notificacion: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    n.id_notificacion,
                    n.titulo,
                    n.mensaje,
                    n.fecha_creacion,
                    n.id_usuario,

                    COUNT(
                        nd.id_destinatario
                    ) AS total_destinatarios,

                    COUNT(
                        nd.id_destinatario
                    ) FILTER (
                        WHERE nd.estado = 'ABIERTO'
                    ) AS total_abiertos,

                    COUNT(
                        nd.id_destinatario
                    ) FILTER (
                        WHERE nd.estado = 'GENERADO'
                    ) AS total_pendientes

                FROM school.notificacion n

                LEFT JOIN
                    school.notificacion_destinatario nd
                    ON nd.id_notificacion =
                       n.id_notificacion

                WHERE n.id_notificacion =
                      :id_notificacion

                GROUP BY
                    n.id_notificacion,
                    n.titulo,
                    n.mensaje,
                    n.fecha_creacion,
                    n.id_usuario
                """
            ),
            {
                "id_notificacion":
                    id_notificacion,
            },
        ).mappings().first()

        if row is None:
            return None

        resultado = dict(row)

        resultado["destinatarios"] = (
            NotificacionRepository
            .list_destinatarios(
                db,
                id_notificacion,
            )
        )

        return resultado

    @staticmethod
    def list_destinatarios(
        db: Session,
        id_notificacion: int,
    ) -> list[dict]:

        rows = db.execute(
            text(
                """
                SELECT
                    nd.id_destinatario,
                    nd.id_contacto,

                    c.nombre AS contacto,

                    c.id_estudiante,

                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante,

                    c.telefono,
                    c.whatsapp,
                    c.email,
                    c.es_principal,

                    nd.estado,
                    nd.fecha_generado,
                    nd.fecha_abierto

                FROM
                    school.notificacion_destinatario nd

                JOIN school.contacto c
                    ON c.id_contacto =
                       nd.id_contacto

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       c.id_estudiante

                WHERE nd.id_notificacion =
                      :id_notificacion

                ORDER BY
                    c.es_principal DESC,
                    c.nombre
                """
            ),
            {
                "id_notificacion":
                    id_notificacion,
            },
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def list(
        db: Session,
        id_estudiante: int | None = None,
        estado_destinatario: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:

        filtros = []
        params = {
            "offset": offset,
            "limit": limit,
        }

        if id_estudiante is not None:
            filtros.append(
                """
                EXISTS (
                    SELECT 1
                    FROM
                        school.notificacion_destinatario nd2
                    JOIN school.contacto c2
                        ON c2.id_contacto =
                           nd2.id_contacto
                    WHERE nd2.id_notificacion =
                          n.id_notificacion
                      AND c2.id_estudiante =
                          :id_estudiante
                )
                """
            )

            params["id_estudiante"] = (
                id_estudiante
            )

        if estado_destinatario is not None:
            filtros.append(
                """
                EXISTS (
                    SELECT 1
                    FROM
                        school.notificacion_destinatario nd3
                    WHERE nd3.id_notificacion =
                          n.id_notificacion
                      AND nd3.estado =
                          :estado_destinatario
                )
                """
            )

            params["estado_destinatario"] = (
                estado_destinatario
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
                    n.id_notificacion,
                    n.titulo,
                    n.mensaje,
                    n.fecha_creacion,
                    n.id_usuario,

                    COUNT(
                        nd.id_destinatario
                    ) AS total_destinatarios,

                    COUNT(
                        nd.id_destinatario
                    ) FILTER (
                        WHERE nd.estado = 'ABIERTO'
                    ) AS total_abiertos,

                    COUNT(
                        nd.id_destinatario
                    ) FILTER (
                        WHERE nd.estado = 'GENERADO'
                    ) AS total_pendientes

                FROM school.notificacion n

                LEFT JOIN
                    school.notificacion_destinatario nd
                    ON nd.id_notificacion =
                       n.id_notificacion

                {where_sql}

                GROUP BY
                    n.id_notificacion,
                    n.titulo,
                    n.mensaje,
                    n.fecha_creacion,
                    n.id_usuario

                ORDER BY
                    n.fecha_creacion DESC,
                    n.id_notificacion DESC

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
    def get_destinatario(
        db: Session,
        id_destinatario: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    nd.id_destinatario,
                    nd.id_notificacion,
                    nd.id_contacto,

                    c.nombre AS contacto,

                    c.id_estudiante,

                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante,

                    c.telefono,
                    c.whatsapp,
                    c.email,
                    c.es_principal,

                    nd.estado,
                    nd.fecha_generado,
                    nd.fecha_abierto

                FROM
                    school.notificacion_destinatario nd

                JOIN school.contacto c
                    ON c.id_contacto =
                       nd.id_contacto

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       c.id_estudiante

                WHERE nd.id_destinatario =
                      :id_destinatario
                """
            ),
            {
                "id_destinatario":
                    id_destinatario,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def marcar_abierto(
        db: Session,
        id_destinatario: int,
    ) -> None:

        db.execute(
            text(
                """
                UPDATE
                    school.notificacion_destinatario
                SET
                    estado = 'ABIERTO',

                    fecha_abierto = COALESCE(
                        fecha_abierto,
                        CURRENT_TIMESTAMP
                    )

                WHERE id_destinatario =
                      :id_destinatario
                """
            ),
            {
                "id_destinatario":
                    id_destinatario,
            },
        )

    @staticmethod
    def buscar_contactos(
        db: Session,
        buscar: str | None = None,
        limit: int = 50,
    ) -> list[dict]:

        filtros = [
            "c.activo = true"
        ]

        params = {
            "limit": limit,
        }

        if buscar:
            filtros.append(
                """
                (
                    e.codigo_estudiante
                        ILIKE :buscar
                    OR CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) ILIKE :buscar
                    OR c.nombre ILIKE :buscar
                    OR COALESCE(
                        c.parentesco,
                        ''
                    ) ILIKE :buscar
                    OR COALESCE(
                        c.telefono,
                        ''
                    ) ILIKE :buscar
                    OR COALESCE(
                        c.whatsapp,
                        ''
                    ) ILIKE :buscar
                    OR COALESCE(
                        c.email,
                        ''
                    ) ILIKE :buscar
                )
                """
            )

            params["buscar"] = (
                f"%{buscar.strip()}%"
            )

        where_sql = (
            "WHERE "
            + " AND ".join(filtros)
        )

        rows = db.execute(
            text(
                f"""
                SELECT
                    c.id_contacto,
                    c.id_estudiante,

                    e.codigo_estudiante,

                    CONCAT(
                        e.nombres,
                        ' ',
                        e.apellidos
                    ) AS estudiante,

                    c.nombre AS contacto,
                    c.parentesco,

                    c.telefono,
                    c.whatsapp,
                    c.email,

                    c.es_principal

                FROM school.contacto c

                JOIN school.estudiante e
                    ON e.id_estudiante =
                       c.id_estudiante

                {where_sql}

                ORDER BY
                    c.es_principal DESC,
                    estudiante,
                    c.nombre

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
    def get_contacto_preferido(
        db: Session,
        id_estudiante: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    id_contacto,
                    id_estudiante,
                    nombre,
                    telefono,
                    whatsapp,
                    email,
                    es_principal,
                    activo

                FROM school.contacto

                WHERE id_estudiante =
                      :id_estudiante
                  AND activo = true

                ORDER BY
                    es_principal DESC,
                    id_contacto

                LIMIT 1
                """
            ),
            {
                "id_estudiante":
                    id_estudiante,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def obtener_deuda_estudiante(
        db: Session,
        id_estudiante: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    id_estudiante,

                    MAX(
                        codigo_estudiante
                    ) AS codigo_estudiante,

                    MAX(
                        estudiante
                    ) AS estudiante,

                    SUM(
                        deuda_total
                    ) AS deuda_total

                FROM
                    school.vw_estudiantes_insolventes

                WHERE id_estudiante =
                      :id_estudiante

                GROUP BY id_estudiante
                """
            ),
            {
                "id_estudiante":
                    id_estudiante,
            },
        ).mappings().first()

        return dict(row) if row else None