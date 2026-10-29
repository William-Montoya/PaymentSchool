from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_empleado: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.empleado.id_empleado",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_usuario_empleado",
        ),
        nullable=True,
    )

    username: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "ACTIVO",
            "INACTIVO",
            "BLOQUEADO",
            name="estado_usuario",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="ACTIVO"
    )

    ultimo_acceso: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    empleado: Mapped["Empleado | None"] = relationship(
        "Empleado",
        back_populates="usuario",
        uselist=False,
    )

    roles: Mapped[list["UsuarioRol"]] = relationship(
        "UsuarioRol",
        back_populates="usuario",
    )

    auditorias: Mapped[list["Auditoria"]] = relationship(
        "Auditoria",
        back_populates="usuario",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_empleado",
            name="uq_usuario_empleado",
        ),
    )