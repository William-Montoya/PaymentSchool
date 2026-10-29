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
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Solvencia(Base):
    __tablename__ = "solvencia"

    id_solvencia: Mapped[int] = mapped_column(
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
            name="fk_solvencia_estudiante",
        ),
        nullable=False,
    )

    id_inscripcion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.inscripcion.id_inscripcion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_solvencia_inscripcion",
        ),
        nullable=False,
    )

    id_evaluacion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.evaluacion.id_evaluacion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_solvencia_evaluacion",
        ),
        nullable=False,
    )

    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    fecha_corte: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    saldo_corte: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "SOLVENTE",
            "INSOLVENTE",
            name="estado_solvencia",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
    )

    codigo_verificacion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="solvencias",
    )

    inscripcion: Mapped["Inscripcion"] = relationship(
        "Inscripcion",
        back_populates="solvencias",
    )

    evaluacion: Mapped["Evaluacion"] = relationship(
        "Evaluacion",
        back_populates="solvencias",
    )

    __table_args__ = (
        UniqueConstraint(
            "codigo_verificacion",
            name="uq_solvencia_codigo",
        ),
        CheckConstraint(
            "saldo_corte >= 0",
            name="ck_solvencia_saldo",
        ),
        Index(
            "idx_solvencia_estudiante",
            "id_estudiante",
        ),
        Index(
            "idx_solvencia_evaluacion",
            "id_evaluacion",
        ),
    )