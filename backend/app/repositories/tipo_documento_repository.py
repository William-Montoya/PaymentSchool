from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tipo_documento import TipoDocumento


class TipoDocumentoRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_tipo_documento: int,
    ) -> TipoDocumento | None:
        return db.get(
            TipoDocumento,
            id_tipo_documento,
        )

    @staticmethod
    def get_by_nombre(
        db: Session,
        nombre: str,
    ) -> TipoDocumento | None:

        stmt = select(TipoDocumento).where(
            TipoDocumento.nombre == nombre
        )

        return db.scalar(stmt)

    @staticmethod
    def list(
        db: Session,
        activo: bool | None = None,
        obligatorio: bool | None = None,
    ) -> list[TipoDocumento]:

        stmt = select(TipoDocumento)

        if activo is not None:
            stmt = stmt.where(
                TipoDocumento.activo == activo
            )

        if obligatorio is not None:
            stmt = stmt.where(
                TipoDocumento.obligatorio
                == obligatorio
            )

        stmt = stmt.order_by(
            TipoDocumento.nombre
        )

        return list(
            db.scalars(stmt).all()
        )