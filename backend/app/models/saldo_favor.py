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
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SaldoFavor(Base):
    __tablename__ = "saldo_favor"

    id_saldo_favor: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_estudiante: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.estudiante.id_estudiante",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_saldo_favor_estudiante",
        ),
        nullable=False,
    )

    id_pago_origen: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.pago.id_pago",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_saldo_favor_pago",
        ),
        nullable=True,
    )

    monto_original: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    monto_disponible: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ACTIVO",
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="saldos_favor",
    )

    pago_origen: Mapped["Pago | None"] = relationship(
        "Pago",
        back_populates="saldos_favor",
    )

    __table_args__ = (
        CheckConstraint(
            "monto_original > 0",
            name="ck_saldo_favor_original",
        ),
        CheckConstraint(
            "monto_disponible >= 0 "
            "AND monto_disponible <= monto_original",
            name="ck_saldo_favor_disponible",
        ),
        CheckConstraint(
            "estado IN ('ACTIVO', 'AGOTADO', 'ANULADO')",
            name="ck_saldo_favor_estado",
        ),
        Index(
            "idx_saldo_favor_estudiante",
            "id_estudiante",
            postgresql_where=text(
                "(estado)::text = 'ACTIVO'::text"
            ),
        ),
        {
            "schema": "school",
        },
    )