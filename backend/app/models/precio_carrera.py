from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PrecioCarrera(Base):
    __tablename__ = "precio_carrera"

    id_precio: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_carrera_ciclo: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.carrera_ciclo.id_carrera_ciclo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_precio_carrera_ciclo",
        ),
        nullable=False,
    )

    id_grado: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.grado.id_grado",
            name="fk_precio_carrera_grado",
        ),
        nullable=True,
    )

    tipo: Mapped[str] = mapped_column(
        Enum(
            "INSCRIPCION",
            "MENSUALIDAD",
            "OTRO",
            name="tipo_precio",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
    )

    concepto: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    monto: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
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

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    carrera_ciclo: Mapped["CarreraCiclo"] = relationship(
        "CarreraCiclo",
        back_populates="precios",
    )

    obligaciones: Mapped[list["Obligacion"]] = relationship(
        "Obligacion",
        back_populates="precio",
    )

    __table_args__ = (
        CheckConstraint(
            "fecha_fin IS NULL OR fecha_fin >= fecha_inicio",
            name="ck_precio_fechas",
        ),
        CheckConstraint(
            "monto >= 0",
            name="ck_precio_monto",
        ),
        Index(
            "ix_precio_carrera_carrera_ciclo_grado_tipo",
            "id_carrera_ciclo",
            "id_grado",
            "tipo",
        ),
    )