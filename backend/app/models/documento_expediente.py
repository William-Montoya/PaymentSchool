from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    Index,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DocumentoExpediente(Base):
    __tablename__ = "documento_expediente"

    id_documento: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_expediente: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.expediente.id_expediente",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    id_tipo_documento: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.tipo_documento.id_tipo_documento",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    nombre_archivo: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    ruta_archivo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    fecha_entrega: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    entregado: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false"
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    expediente: Mapped["Expediente"] = relationship(
        "Expediente",
        back_populates="documentos",
    )

    tipo_documento: Mapped["TipoDocumento"] = relationship(
        "TipoDocumento",
        back_populates="documentos_expediente",
    )

    __table_args__ = (
        Index(
            "idx_documento_expediente",
            "id_expediente",
        ),
    )