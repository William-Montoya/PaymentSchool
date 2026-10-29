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
    Index,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MovimientoSaldo(Base):
    __tablename__ = "movimiento_saldo"

    id_movimiento: Mapped[int] = mapped_column(
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
            name="fk_movimiento_estudiante",
        ),
        nullable=False,
    )

    id_inscripcion_origen: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.inscripcion.id_inscripcion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_movimiento_origen",
        ),
        nullable=True,
    )

    id_inscripcion_destino: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.inscripcion.id_inscripcion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_movimiento_destino",
        ),
        nullable=True,
    )

    tipo: Mapped[str] = mapped_column(
        Enum(
            "TRASLADO_SALDO",
            "AJUSTE",
            "DEVOLUCION",
            "COMPENSACION",
            name="tipo_movimiento_saldo",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
    )

    monto: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    fecha_movimiento: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    motivo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "PENDIENTE",
            "APLICADO",
            "ANULADO",
            name="estado_movimiento_saldo",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="PENDIENTE",
    )

    id_usuario: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    referencia: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="movimientos_saldo",
    )

    inscripcion_origen: Mapped["Inscripcion | None"] = relationship(
        "Inscripcion",
        foreign_keys=[id_inscripcion_origen],
        back_populates="movimientos_saldo_origen",
    )

    inscripcion_destino: Mapped["Inscripcion | None"] = relationship(
        "Inscripcion",
        foreign_keys=[id_inscripcion_destino],
        back_populates="movimientos_saldo_destino",
    )

    __table_args__ = (
        CheckConstraint(
            "monto > 0",
            name="ck_movimiento_monto",
        ),

        Index(
            "idx_movimiento_destino",
            "id_inscripcion_destino",
        ),

        Index(
            "idx_movimiento_estudiante",
            "id_estudiante",
        ),

        Index(
            "idx_movimiento_origen",
            "id_inscripcion_origen",
        ),

    )