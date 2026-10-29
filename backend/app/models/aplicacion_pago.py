from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    Index,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AplicacionPago(Base):
    __tablename__ = "aplicacion_pago"

    id_aplicacion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_pago: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.pago.id_pago",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_aplicacion_pago",
        ),
        nullable=False,
    )

    id_obligacion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.obligacion.id_obligacion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_aplicacion_obligacion",
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
        server_default=func.current_timestamp(),
    )

    pago: Mapped["Pago"] = relationship(
        "Pago",
        back_populates="aplicaciones",
    )

    obligacion: Mapped["Obligacion"] = relationship(
        "Obligacion",
        back_populates="aplicaciones",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_pago",
            "id_obligacion",
            name="uq_aplicacion_pago_obligacion",
        ),
        CheckConstraint(
            "monto_aplicado > 0",
            name="ck_aplicacion_monto",
        ),
        Index(
            "idx_aplicacion_obligacion",
            "id_obligacion",
        ),
        Index(
            "idx_aplicacion_pago",
            "id_pago",
        ),
    )