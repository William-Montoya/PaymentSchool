from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.documento_expediente import (
    DocumentoExpediente,
)


class DocumentoExpedienteRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_documento: int,
    ) -> DocumentoExpediente | None:

        return db.get(
            DocumentoExpediente,
            id_documento,
        )

    @staticmethod
    def get_by_expediente_tipo(
        db: Session,
        id_expediente: int,
        id_tipo_documento: int,
    ) -> DocumentoExpediente | None:

        stmt = (
            select(
                DocumentoExpediente
            )
            .where(
                DocumentoExpediente.id_expediente
                == id_expediente,

                DocumentoExpediente.id_tipo_documento
                == id_tipo_documento,
            )
        )

        return db.scalar(stmt)

    @staticmethod
    def crear(
        db: Session,
        documento: DocumentoExpediente,
    ) -> DocumentoExpediente:

        db.add(documento)
        db.flush()
        db.refresh(documento)

        return documento

    @staticmethod
    def list_by_expediente(
        db: Session,
        id_expediente: int,
    ) -> list[DocumentoExpediente]:

        stmt = (
            select(
                DocumentoExpediente
            )
            .where(
                DocumentoExpediente.id_expediente
                == id_expediente
            )
            .order_by(
                DocumentoExpediente.id_documento
            )
        )

        return list(
            db.scalars(stmt).all()
        )