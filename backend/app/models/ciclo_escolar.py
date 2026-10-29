from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CicloEscolar(Base):
    __tablename__ = "ciclo_escolar"

    id_ciclo: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    fecha_fin: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "PLANIFICADO",
            "ACTIVO",
            "CERRADO",
            name="estado_ciclo",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="PLANIFICADO",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    carrera_ciclos: Mapped[list["CarreraCiclo"]] = relationship(
        "CarreraCiclo",
        back_populates="ciclo",
    )
    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        "Evaluacion",
        back_populates="ciclo",
    )
    __table_args__ = (
        CheckConstraint(
            "fecha_fin >= fecha_inicio",
            name="ck_ciclo_fechas",
        ),
    )