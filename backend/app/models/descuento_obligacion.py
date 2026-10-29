from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DescuentoObligacion(Base):
    __tablename__ = "descuento_obligacion"

    id_descuento_obligacion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_descuento: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.descuento.id_descuento",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_descuento_obligacion_descuento",
        ),
        nullable=False,
    )

    id_obligacion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.obligacion.id_obligacion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_descuento_obligacion_obligacion",
        ),
        nullable=False,
    )

    monto_aplicado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    fecha_aplicacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    descuento: Mapped["Descuento"] = relationship(
        "Descuento",
        back_populates="descuentos_obligaciones",
    )

    obligacion: Mapped["Obligacion"] = relationship(
        "Obligacion",
        back_populates="descuentos",
    )

    __table_args__ = (
        CheckConstraint(
            "monto_aplicado > 0",
            name="ck_descuento_aplicado",
        ),
    )