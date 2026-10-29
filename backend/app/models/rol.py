from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    String,
    Text,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rol(Base):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true"
    )

    usuarios: Mapped[list["UsuarioRol"]] = relationship(
        "UsuarioRol",
        back_populates="rol",
    )

    permisos: Mapped[list["RolPermiso"]] = relationship(
        "RolPermiso",
        back_populates="rol",
    )

    __table_args__ = (
        UniqueConstraint(
            "nombre",
            name="uq_rol_nombre",
        ),
    )