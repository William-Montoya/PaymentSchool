from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Pago(Base):
    __tablename__ = "pago"

    id_pago: Mapped[int] = mapped_column(
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
            name="fk_pago_estudiante",
        ),
        nullable=False,
    )

    id_usuario: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    fecha_pago: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    monto_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    metodo: Mapped[str] = mapped_column(
        Enum(
            "EFECTIVO",
            "TRANSFERENCIA",
            "DEPOSITO",
            "TARJETA",
            "OTRO",
            name="metodo_pago",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
    )

    referencia: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "PENDIENTE",
            "CONFIRMADO",
            "ANULADO",
            name="estado_pago",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="CONFIRMADO",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="pagos",
    )

    aplicaciones: Mapped[list["AplicacionPago"]] = relationship(
        "AplicacionPago",
        back_populates="pago",
    )
    saldos_favor: Mapped[list["SaldoFavor"]] = relationship(
        "SaldoFavor",
        back_populates="pago_origen",
    )
    recibo: Mapped["Recibo | None"] = relationship(
        "Recibo",
        back_populates="pago",
        uselist=False,
    )

    __table_args__ = (
        CheckConstraint(
            "monto_total > 0",
            name="ck_pago_monto",
        ),
        Index(
            "idx_pago_estudiante",
            "id_estudiante",
        ),

        Index(
            "idx_pago_fecha",
            "fecha_pago",
        ),
    )