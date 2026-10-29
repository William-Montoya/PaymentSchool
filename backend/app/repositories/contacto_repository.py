from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.contacto import Contacto


class ContactoRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_contacto: int,
    ) -> Contacto | None:

        return db.get(
            Contacto,
            id_contacto,
        )

    @staticmethod
    def list_by_estudiante(
        db: Session,
        id_estudiante: int,
        activo: bool | None = None,
    ) -> list[Contacto]:

        stmt = select(Contacto).where(
            Contacto.id_estudiante
            == id_estudiante
        )

        if activo is not None:
            stmt = stmt.where(
                Contacto.activo == activo
            )

        stmt = stmt.order_by(
            Contacto.es_principal.desc(),
            Contacto.nombre,
        )

        return list(
            db.scalars(stmt).all()
        )

    @staticmethod
    def quitar_principal(
        db: Session,
        id_estudiante: int,
        excluir_id: int | None = None,
    ) -> None:

        stmt = (
            update(Contacto)
            .where(
                Contacto.id_estudiante
                == id_estudiante,

                Contacto.es_principal.is_(True),
            )
            .values(
                es_principal=False
            )
        )

        if excluir_id is not None:
            stmt = stmt.where(
                Contacto.id_contacto
                != excluir_id
            )

        db.execute(stmt)