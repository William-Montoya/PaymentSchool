from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
    Index,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Obligacion(Base):
    __tablename__ = "obligacion"

    id_obligacion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_inscripcion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.inscripcion.id_inscripcion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_obligacion_inscripcion",
        ),
        nullable=False,
    )

    id_precio: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.precio_carrera.id_precio",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_obligacion_precio",
        ),
        nullable=True,
    )

    concepto: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    periodo: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    fecha_vencimiento: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    monto_bruto: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    monto_descuento: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0",
    )

    monto_beca: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0",
    )

    monto_neto: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "PENDIENTE",
            "PARCIAL",
            "PAGADA",
            "ANULADA",
            name="estado_obligacion",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="PENDIENTE",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    tipo_obligacion: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    inscripcion: Mapped["Inscripcion"] = relationship(
        "Inscripcion",
        back_populates="obligaciones",
    )

    precio: Mapped["PrecioCarrera | None"] = relationship(
        "PrecioCarrera",
        back_populates="obligaciones",
    )

    aplicaciones: Mapped[list["AplicacionPago"]] = relationship(
        "AplicacionPago",
        back_populates="obligacion",
    )
    descuentos: Mapped[list["DescuentoObligacion"]] = relationship(
        "DescuentoObligacion",
        back_populates="obligacion",
    )
    beca_aplicacion: Mapped["BecaObligacion | None"] = relationship(
        "BecaObligacion",
        back_populates="obligacion",
        uselist=False,
    )

    __table_args__ = (
        CheckConstraint(
            "monto_beca >= 0",
            name="ck_obligacion_beca",
        ),
        CheckConstraint(
            "monto_bruto >= 0",
            name="ck_obligacion_bruto",
        ),
        CheckConstraint(
            "monto_descuento >= 0",
            name="ck_obligacion_descuento",
        ),
        CheckConstraint(
            "(monto_descuento + monto_beca) <= monto_bruto",
            name="ck_obligacion_descuentos",
        ),
        CheckConstraint(
            "monto_neto >= 0",
            name="ck_obligacion_neto",
        ),
        CheckConstraint(
            "tipo_obligacion IN "
            "('INSCRIPCION', 'MENSUALIDAD', 'CERTIFICACION', "
            "'CONSTANCIA', 'OTRO')",
            name="ck_obligacion_tipo",
        ),

        Index(
            "idx_obligacion_fecha_vencimiento",
            "fecha_vencimiento",
        ),

        Index(
            "idx_obligacion_inscripcion",
            "id_inscripcion",
        ),
        Index(
            "idx_obligacion_pendiente",
            "id_inscripcion",
            postgresql_where=text(
                "estado IN ('PENDIENTE'::school.estado_obligacion, "
                "'PARCIAL'::school.estado_obligacion)"
            ),
        ),
        Index(
            "uq_obligacion_mensualidad_periodo",
            "id_inscripcion",
            "periodo",
            unique=True,
            postgresql_where=text(
                "(tipo_obligacion)::text = 'MENSUALIDAD'::text"
            ),
        ),
    )