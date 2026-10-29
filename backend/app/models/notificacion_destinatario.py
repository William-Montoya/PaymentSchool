from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String,func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NotificacionDestinatario(Base):
    __tablename__ = "notificacion_destinatario"

    id_destinatario: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_notificacion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.notificacion.id_notificacion",
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="fk_notificacion_destinatario",
        ),
        nullable=False,
    )

    id_contacto: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.contacto.id_contacto",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_notificacion_contacto",
        ),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="GENERADO"
    )

    fecha_generado: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    fecha_abierto: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Relaciones
    notificacion: Mapped["Notificacion"] = relationship(
        "Notificacion",
        back_populates="destinatarios",
    )

    contacto: Mapped["Contacto"] = relationship(
        "Contacto",
        back_populates="notificaciones",
    )