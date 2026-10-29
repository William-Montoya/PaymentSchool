from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.empleado import Empleado


class EmpleadoRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_empleado: int,
    ) -> Empleado | None:

        return db.get(
            Empleado,
            id_empleado,
        )

    @staticmethod
    def list(
        db: Session,
        activo: bool | None = None,
    ) -> list[Empleado]:

        stmt = select(Empleado)

        if activo is not None:
            stmt = stmt.where(
                Empleado.activo == activo
            )

        stmt = stmt.order_by(
            Empleado.apellidos,
            Empleado.nombres,
        )

        return list(
            db.scalars(stmt).all()
        )