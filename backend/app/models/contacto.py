from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    String,
    Index,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Contacto(Base):
    __tablename__ = "contacto"

    id_contacto: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_estudiante: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.estudiante.id_estudiante",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    parentesco: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    telefono: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    whatsapp: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    es_principal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false"
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true"
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="contactos",
    )
    notificaciones: Mapped[list["NotificacionDestinatario"]] = relationship(
        "NotificacionDestinatario",
        back_populates="contacto",
    )

    __table_args__ = (
        Index(
            "idx_contacto_estudiante",
            "id_estudiante",
        ),
    )