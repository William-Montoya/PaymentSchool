from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BecaObligacion(Base):
    __tablename__ = "beca_obligacion"

    id_beca_obligacion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_beca_estudiante: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.beca_estudiante.id_beca_estudiante",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_beca_obligacion_beca_estudiante",
        ),
        nullable=False,
    )

    id_obligacion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.obligacion.id_obligacion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_beca_obligacion_obligacion",
        ),
        nullable=False,
    )

    porcentaje_aplicado: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    monto_aplicado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    fecha_aplicacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    beca_estudiante: Mapped["BecaEstudiante"] = relationship(
        "BecaEstudiante",
        back_populates="aplicaciones",
    )

    obligacion: Mapped["Obligacion"] = relationship(
        "Obligacion",
        back_populates="beca_aplicacion",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_obligacion",
            name="uq_beca_obligacion_obligacion",
        ),
        CheckConstraint(
            "porcentaje_aplicado >= 0 "
            "AND porcentaje_aplicado <= 100",
            name="ck_beca_obligacion_porcentaje",
        ),
        CheckConstraint(
            "monto_aplicado >= 0",
            name="ck_beca_obligacion_monto",
        ),
        Index(
            "idx_beca_obligacion_beca_estudiante",
            "id_beca_estudiante",
        ),
        {"schema": "school"},
    )