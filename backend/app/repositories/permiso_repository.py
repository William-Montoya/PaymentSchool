from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.permiso import Permiso


class PermisoRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_permiso: int,
    ) -> Permiso | None:

        return db.get(
            Permiso,
            id_permiso,
        )

    @staticmethod
    def get_by_nombre(
        db: Session,
        nombre: str,
    ) -> Permiso | None:

        stmt = select(Permiso).where(
            func.upper(Permiso.nombre)
            == nombre.upper()
        )

        return db.scalar(stmt)

    @staticmethod
    def list(
        db: Session,
    ) -> list[Permiso]:

        stmt = (
            select(Permiso)
            .order_by(Permiso.nombre)
        )

        return list(
            db.scalars(stmt).all()
        )