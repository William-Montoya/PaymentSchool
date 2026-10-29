from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.estudiante import Estudiante


class EstudianteRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_estudiante: int,
    ) -> Estudiante | None:
        return db.get(Estudiante, id_estudiante)

    @staticmethod
    def get_by_codigo(
        db: Session,
        codigo_estudiante: str,
    ) -> Estudiante | None:
        stmt = select(Estudiante).where(
            Estudiante.codigo_estudiante == codigo_estudiante
        )
        return db.scalar(stmt)

    @staticmethod
    def get_by_cui(
        db: Session,
        cui: str,
    ) -> Estudiante | None:
        stmt = select(Estudiante).where(
            Estudiante.cui == cui
        )
        return db.scalar(stmt)

    @staticmethod
    def list(
        db: Session,
        offset: int = 0,
        limit: int = 50,
        estado: str | None = None,
        buscar: str | None = None,
    ) -> list[Estudiante]:
        stmt = select(Estudiante)

        if estado:
            stmt = stmt.where(
                Estudiante.estado == estado
            )

        if buscar:
            patron = f"%{buscar.strip()}%"
            stmt = stmt.where(
                or_(
                    Estudiante.codigo_estudiante.ilike(patron),
                    Estudiante.nombres.ilike(patron),
                    Estudiante.apellidos.ilike(patron),
                    Estudiante.cui.ilike(patron),
                )
            )

        stmt = (
            stmt
            .order_by(
                Estudiante.apellidos,
                Estudiante.nombres,
            )
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(stmt).all())

    @staticmethod
    def create(
        db: Session,
        estudiante: Estudiante,
    ) -> Estudiante:
        db.add(estudiante)
        db.flush()
        db.refresh(estudiante)
        return estudiante

    @staticmethod
    def save(
        db: Session,
        estudiante: Estudiante,
    ) -> Estudiante:
        db.flush()
        db.refresh(estudiante)
        return estudiante