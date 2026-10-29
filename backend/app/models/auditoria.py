from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text,func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_usuario: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.usuario.id_usuario",
            onupdate="CASCADE",
            ondelete="SET NULL",
            name="fk_auditoria_usuario",
        ),
        nullable=True,
    )

    fecha_evento: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    modulo: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    accion: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    tabla_afectada: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    id_registro: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    datos_anteriores: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    datos_nuevos: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    usuario: Mapped["Usuario | None"] = relationship(
        "Usuario",
        back_populates="auditorias",
    )

    __table_args__ = (
        Index(
            "idx_auditoria_fecha",
            "fecha_evento",
        ),
        Index(
            "idx_auditoria_usuario",
            "id_usuario",
        ),
    )