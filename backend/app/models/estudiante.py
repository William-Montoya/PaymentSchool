from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base


class Estudiante(Base):
    __tablename__ = "estudiante"

    id_estudiante: Mapped[int] = (
        mapped_column(
            BigInteger,
            primary_key=True,
            autoincrement=True,
        )
    )

    codigo_estudiante: Mapped[str] = (
        mapped_column(
            String(50),
            nullable=False,
            unique=True,
            server_default=text(
                "("
                "'EST-'::text || "
                "lpad("
                "("
                "nextval("
                "'school.seq_codigo_estudiante'::regclass"
                ")"
                ")::text, "
                "6, "
                "'0'::text"
                ")"
                ")"
            ),
        )
    )

    cui: Mapped[str | None] = (
        mapped_column(
            String(30),
            nullable=True,
            unique=True,
        )
    )

    nombres: Mapped[str] = (
        mapped_column(
            String(100),
            nullable=False,
        )
    )

    apellidos: Mapped[str] = (
        mapped_column(
            String(100),
            nullable=False,
        )
    )

    fecha_nacimiento: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True,
    )

    telefono: Mapped[str | None] = (
        mapped_column(
            String(30),
            nullable=True,
        )
    )

    whatsapp: Mapped[str | None] = (
        mapped_column(
            String(30),
            nullable=True,
        )
    )

    email: Mapped[str | None] = (
        mapped_column(
            String(150),
            nullable=True,
        )
    )

    direccion: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )

    estado: Mapped[str] = (
        mapped_column(
            Enum(
                "ACTIVO",
                "INACTIVO",
                "RETIRADO",
                "EGRESADO",
                name="estado_estudiante",
                schema="school",
                native_enum=True,
                create_type=False,
            ),
            nullable=False,
            server_default="ACTIVO",
        )
    )

    creado_en: Mapped[datetime] = (
        mapped_column(
            DateTime,
            server_default=
                func.current_timestamp(),
            nullable=False,
        )
    )

    actualizado_en: Mapped[
        datetime
    ] = mapped_column(
        DateTime,
        server_default=
            func.current_timestamp(),
        nullable=False,
    )

    inscripciones: Mapped[
        list["Inscripcion"]
    ] = relationship(
        "Inscripcion",
        back_populates="estudiante",
    )

    expediente: Mapped[
        "Expediente | None"
    ] = relationship(
        "Expediente",
        back_populates="estudiante",
        uselist=False,
    )

    contactos: Mapped[
        list["Contacto"]
    ] = relationship(
        "Contacto",
        back_populates="estudiante",
    )

    pagos: Mapped[
        list["Pago"]
    ] = relationship(
        "Pago",
        back_populates="estudiante",
    )

    becas: Mapped[
        list["BecaEstudiante"]
    ] = relationship(
        "BecaEstudiante",
        back_populates="estudiante",
    )

    cambios_carrera: Mapped[
        list["CambioCarrera"]
    ] = relationship(
        "CambioCarrera",
        back_populates="estudiante",
    )

    saldos_favor: Mapped[
        list["SaldoFavor"]
    ] = relationship(
        "SaldoFavor",
        back_populates="estudiante",
    )

    movimientos_saldo: Mapped[
        list["MovimientoSaldo"]
    ] = relationship(
        "MovimientoSaldo",
        back_populates="estudiante",
    )

    solvencias: Mapped[
        list["Solvencia"]
    ] = relationship(
        "Solvencia",
        back_populates="estudiante",
    )

    __table_args__ = (
        Index(
            "idx_estudiante_activo",
            "id_estudiante",
            postgresql_where=text(
                "estado = "
                "'ACTIVO'::"
                "school.estado_estudiante"
            ),
        ),
    )