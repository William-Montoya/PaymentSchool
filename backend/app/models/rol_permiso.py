from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    id_rol: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.rol.id_rol",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_rol_permiso_rol",
        ),
        primary_key=True,
    )

    id_permiso: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.permiso.id_permiso",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_rol_permiso_permiso",
        ),
        primary_key=True,
    )

    rol: Mapped["Rol"] = relationship(
        "Rol",
        back_populates="permisos",
    )

    permiso: Mapped["Permiso"] = relationship(
        "Permiso",
        back_populates="roles",
    )