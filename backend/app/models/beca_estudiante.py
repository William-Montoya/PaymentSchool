from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BecaEstudiante(Base):
    __tablename__ = "beca_estudiante"

    id_beca_estudiante: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_beca: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.beca.id_beca",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_beca_estudiante_beca",
        ),
        nullable=False,
    )

    id_estudiante: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.estudiante.id_estudiante",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_beca_estudiante_estudiante",
        ),
        nullable=False,
    )

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    fecha_fin: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    porcentaje_aplicado: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    beca: Mapped["Beca"] = relationship(
        "Beca",
        back_populates="estudiantes",
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="becas",
    )
    aplicaciones: Mapped[list["BecaObligacion"]] = relationship(
        "BecaObligacion",
        back_populates="beca_estudiante",
    )

    __table_args__ = (
        CheckConstraint(
            "porcentaje_aplicado IS NULL OR "
            "(porcentaje_aplicado >= 0 AND "
            "porcentaje_aplicado <= 100)",
            name="ck_beca_estudiante_porcentaje",
        ),
    )