from __future__ import annotations

from sqlalchemy import BigInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Permiso(Base):
    __tablename__ = "permiso"

    id_permiso: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relaciones
    roles: Mapped[list["RolPermiso"]] = relationship(
        "RolPermiso",
        back_populates="permiso",
    )

    __table_args__ = (
        UniqueConstraint(
            "nombre",
            name="uq_permiso_nombre",
        ),
    )