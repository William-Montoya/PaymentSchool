from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text,func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Carrera(Base):
    __tablename__ = "carrera"

    id_carrera: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    carrera_ciclos: Mapped[list["CarreraCiclo"]] = relationship(
        "CarreraCiclo",
        back_populates="carrera",
    )