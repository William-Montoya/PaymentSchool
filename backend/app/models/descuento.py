from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Descuento(Base):
    __tablename__ = "descuento"

    id_descuento: Mapped[int] = mapped_column(
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

    porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    monto_fijo: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true"
    )

    descuentos_obligaciones: Mapped[
        list["DescuentoObligacion"]
    ] = relationship(
        "DescuentoObligacion",
        back_populates="descuento",
    )

    __table_args__ = (
        UniqueConstraint(
            "nombre",
            name="uq_descuento_nombre",
        ),
        CheckConstraint(
            "monto_fijo IS NULL OR monto_fijo >= 0",
            name="ck_descuento_monto",
        ),
        CheckConstraint(
            "porcentaje IS NULL OR "
            "(porcentaje >= 0 AND porcentaje <= 100)",
            name="ck_descuento_porcentaje",
        ),
        CheckConstraint(
            "porcentaje IS NOT NULL OR monto_fijo IS NOT NULL",
            name="ck_descuento_tipo",
        ),
    )