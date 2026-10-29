from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    Enum,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Beca(Base):
    __tablename__ = "beca"

    id_beca: Mapped[int] = mapped_column(
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

    porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    convenio: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "PENDIENTE",
            "ACTIVA",
            "FINALIZADA",
            "CANCELADA",
            name="estado_beca",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="ACTIVA"
    )

    fecha_inicio: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    fecha_fin: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    estudiantes: Mapped[list["BecaEstudiante"]] = relationship(
        "BecaEstudiante",
        back_populates="beca",
    )

    __table_args__ = (
        UniqueConstraint(
            "nombre",
            name="uq_beca_nombre",
        ),
        CheckConstraint(
            "fecha_fin IS NULL OR "
            "fecha_inicio IS NULL OR "
            "fecha_fin >= fecha_inicio",
            name="ck_beca_fechas",
        ),
        CheckConstraint(
            "porcentaje >= 0 AND porcentaje <= 100",
            name="ck_beca_porcentaje",
        ),
    )