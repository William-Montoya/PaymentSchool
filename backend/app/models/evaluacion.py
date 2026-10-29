from __future__ import annotations

from datetime import date

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    String,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Evaluacion(Base):
    __tablename__ = "evaluacion"

    id_evaluacion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_ciclo: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.ciclo_escolar.id_ciclo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_evaluacion_ciclo",
        ),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    fecha_evaluacion: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    fecha_corte_finanzas: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    ciclo: Mapped["CicloEscolar"] = relationship(
        "CicloEscolar",
        back_populates="evaluaciones",
    )

    solvencias: Mapped[list["Solvencia"]] = relationship(
        "Solvencia",
        back_populates="evaluacion",
    )