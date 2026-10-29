from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.rol import Rol


class RolRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_rol: int,
    ) -> Rol | None:

        return db.get(
            Rol,
            id_rol,
        )

    @staticmethod
    def get_by_nombre(
        db: Session,
        nombre: str,
    ) -> Rol | None:

        stmt = select(Rol).where(
            func.upper(Rol.nombre)
            == nombre.upper()
        )

        return db.scalar(stmt)

    @staticmethod
    def list(
        db: Session,
        activo: bool | None = None,
    ) -> list[Rol]:

        stmt = select(Rol)

        if activo is not None:
            stmt = stmt.where(
                Rol.activo == activo
            )

        stmt = stmt.order_by(
            Rol.nombre
        )

        return list(
            db.scalars(stmt).all()
        )

    @staticmethod
    def get_detalle(
        db: Session,
        id_rol: int,
    ) -> dict | None:

        rol = db.execute(
            text(
                """
                SELECT
                    id_rol,
                    nombre,
                    descripcion,
                    activo
                FROM school.rol
                WHERE id_rol = :id_rol
                """
            ),
            {
                "id_rol": id_rol,
            },
        ).mappings().first()

        if rol is None:
            return None

        permisos = db.execute(
            text(
                """
                SELECT
                    p.id_permiso,
                    p.nombre,
                    p.descripcion
                FROM school.rol_permiso rp
                JOIN school.permiso p
                    ON p.id_permiso =
                       rp.id_permiso
                WHERE rp.id_rol = :id_rol
                ORDER BY p.nombre
                """
            ),
            {
                "id_rol": id_rol,
            },
        ).mappings().all()

        resultado = dict(rol)

        resultado["permisos"] = [
            dict(item)
            for item in permisos
        ]

        return resultado

    @staticmethod
    def reemplazar_permisos(
        db: Session,
        id_rol: int,
        ids_permiso: list[int],
    ) -> None:

        db.execute(
            text(
                """
                DELETE FROM school.rol_permiso
                WHERE id_rol = :id_rol
                """
            ),
            {
                "id_rol": id_rol,
            },
        )

        for id_permiso in ids_permiso:

            db.execute(
                text(
                    """
                    INSERT INTO school.rol_permiso (
                        id_rol,
                        id_permiso
                    )
                    VALUES (
                        :id_rol,
                        :id_permiso
                    )
                    """
                ),
                {
                    "id_rol": id_rol,
                    "id_permiso":
                        id_permiso,
                },
            )