from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"

    id_usuario: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.usuario.id_usuario",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_usuario_rol_usuario",
        ),
        primary_key=True,
    )

    id_rol: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.rol.id_rol",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_usuario_rol_rol",
        ),
        primary_key=True,
    )

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="roles",
    )

    rol: Mapped["Rol"] = relationship(
        "Rol",
        back_populates="usuarios",
    )