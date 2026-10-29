from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_usuario: int,
    ) -> Usuario | None:

        return db.get(
            Usuario,
            id_usuario,
        )

    @staticmethod
    def get_by_username(
        db: Session,
        username: str,
    ) -> Usuario | None:

        stmt = select(Usuario).where(
            func.lower(Usuario.username)
            == username.lower()
        )

        return db.scalar(stmt)

    @staticmethod
    def get_by_empleado(
        db: Session,
        id_empleado: int,
    ) -> Usuario | None:

        stmt = select(Usuario).where(
            Usuario.id_empleado
            == id_empleado
        )

        return db.scalar(stmt)

    @staticmethod
    def get_detalle(
        db: Session,
        id_usuario: int,
    ) -> dict | None:

        usuario = db.execute(
            text(
                """
                SELECT
                    u.id_usuario,
                    u.id_empleado,

                    CASE
                        WHEN e.id_empleado IS NULL
                            THEN NULL
                        ELSE CONCAT(
                            e.nombres,
                            ' ',
                            e.apellidos
                        )
                    END AS empleado,

                    e.cargo,

                    u.username,
                    u.estado::text AS estado,
                    u.ultimo_acceso,
                    u.creado_en

                FROM school.usuario u

                LEFT JOIN school.empleado e
                    ON e.id_empleado =
                       u.id_empleado

                WHERE u.id_usuario =
                      :id_usuario
                """
            ),
            {
                "id_usuario": id_usuario,
            },
        ).mappings().first()

        if usuario is None:
            return None

        roles = db.execute(
            text(
                """
                SELECT
                    r.id_rol,
                    r.nombre,
                    r.descripcion,
                    r.activo

                FROM school.usuario_rol ur

                JOIN school.rol r
                    ON r.id_rol = ur.id_rol

                WHERE ur.id_usuario =
                      :id_usuario

                ORDER BY r.nombre
                """
            ),
            {
                "id_usuario": id_usuario,
            },
        ).mappings().all()

        permisos = db.execute(
            text(
                """
                SELECT DISTINCT
                    p.id_permiso,
                    p.nombre,
                    p.descripcion

                FROM school.usuario_rol ur

                JOIN school.rol r
                    ON r.id_rol =
                       ur.id_rol
                   AND r.activo = true

                JOIN school.rol_permiso rp
                    ON rp.id_rol =
                       r.id_rol

                JOIN school.permiso p
                    ON p.id_permiso =
                       rp.id_permiso

                WHERE ur.id_usuario =
                      :id_usuario

                ORDER BY p.nombre
                """
            ),
            {
                "id_usuario": id_usuario,
            },
        ).mappings().all()

        resultado = dict(usuario)

        resultado["roles"] = [
            dict(item)
            for item in roles
        ]

        resultado["permisos"] = [
            dict(item)
            for item in permisos
        ]

        return resultado

    @staticmethod
    def list_ids(
        db: Session,
        estado: str | None = None,
    ) -> list[int]:

        params = {}
        where_sql = ""

        if estado is not None:
            where_sql = (
                "WHERE estado::text = :estado"
            )
            params["estado"] = estado

        return list(
            db.execute(
                text(
                    f"""
                    SELECT id_usuario
                    FROM school.usuario
                    {where_sql}
                    ORDER BY username
                    """
                ),
                params,
            ).scalars().all()
        )

    @staticmethod
    def reemplazar_roles(
        db: Session,
        id_usuario: int,
        ids_rol: list[int],
    ) -> None:

        db.execute(
            text(
                """
                DELETE FROM school.usuario_rol
                WHERE id_usuario = :id_usuario
                """
            ),
            {
                "id_usuario": id_usuario,
            },
        )

        for id_rol in ids_rol:

            db.execute(
                text(
                    """
                    INSERT INTO school.usuario_rol (
                        id_usuario,
                        id_rol
                    )
                    VALUES (
                        :id_usuario,
                        :id_rol
                    )
                    """
                ),
                {
                    "id_usuario":
                        id_usuario,
                    "id_rol":
                        id_rol,
                },
            )

    @staticmethod
    def tiene_permiso(
        db: Session,
        id_usuario: int,
        permiso: str,
    ) -> bool:

        resultado = db.scalar(
            text(
                """
                SELECT EXISTS (
                    SELECT 1

                    FROM school.usuario_rol ur

                    JOIN school.rol r
                        ON r.id_rol =
                           ur.id_rol
                       AND r.activo = true

                    JOIN school.rol_permiso rp
                        ON rp.id_rol =
                           r.id_rol

                    JOIN school.permiso p
                        ON p.id_permiso =
                           rp.id_permiso

                    WHERE ur.id_usuario =
                          :id_usuario

                      AND UPPER(p.nombre) =
                          UPPER(:permiso)
                )
                """
            ),
            {
                "id_usuario": id_usuario,
                "permiso": permiso,
            },
        )

        return bool(resultado)