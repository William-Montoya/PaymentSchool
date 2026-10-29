from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    func,
    Index,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Inscripcion(Base):
    __tablename__ = "inscripcion"

    id_inscripcion: Mapped[int] = mapped_column(
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
        ),
        nullable=False,
    )

    id_carrera_ciclo: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.carrera_ciclo.id_carrera_ciclo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    id_grado: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.grado.id_grado",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    fecha_inscripcion: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    tipo: Mapped[str] = mapped_column(
        Enum(
            "NUEVA",
            "REINSCRIPCION",
            "TRASLADO",
            name="tipo_inscripcion",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="NUEVA",
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "ACTIVA",
            "FINALIZADA",
            "CANCELADA",
            "RETIRADA",
            name="estado_inscripcion",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="ACTIVA",
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="inscripciones",
    )

    carrera_ciclo: Mapped["CarreraCiclo"] = relationship(
        "CarreraCiclo",
        back_populates="inscripciones",
    )

    grado: Mapped["Grado"] = relationship(
        "Grado",
        back_populates="inscripciones",
    )
    obligaciones: Mapped[list["Obligacion"]] = relationship(
        "Obligacion",
        back_populates="inscripcion",
    )
    cambios_carrera_origen: Mapped[list["CambioCarrera"]] = relationship(
        "CambioCarrera",
        foreign_keys="CambioCarrera.id_inscripcion_origen",
        back_populates="inscripcion_origen",
    )

    cambios_carrera_destino: Mapped[list["CambioCarrera"]] = relationship(
        "CambioCarrera",
        foreign_keys="CambioCarrera.id_inscripcion_destino",
        back_populates="inscripcion_destino",
    )
    movimientos_saldo_origen: Mapped[list["MovimientoSaldo"]] = relationship(
        "MovimientoSaldo",
        foreign_keys="MovimientoSaldo.id_inscripcion_origen",
        back_populates="inscripcion_origen",
    )

    movimientos_saldo_destino: Mapped[list["MovimientoSaldo"]] = relationship(
        "MovimientoSaldo",
        foreign_keys="MovimientoSaldo.id_inscripcion_destino",
        back_populates="inscripcion_destino",
    )
    solvencias: Mapped[list["Solvencia"]] = relationship(
        "Solvencia",
        back_populates="inscripcion",
    )

    __table_args__ = (
        Index(
            "idx_inscripcion_activa",
            "id_estudiante",
            postgresql_where=text(
                "estado = 'ACTIVA'::school.estado_inscripcion"
            ),
        ),

        Index(
            "idx_inscripcion_carrera_ciclo",
            "id_carrera_ciclo",
        ),

        Index(
            "idx_inscripcion_estudiante",
            "id_estudiante",
        ),

        Index(
            "idx_inscripcion_grado",
            "id_grado",
        ),
        Index(
            "uq_inscripcion_activa_estudiante_ciclo",
            "id_estudiante",
            "id_carrera_ciclo",
            unique=True,
            postgresql_where=text(
                "estado = 'ACTIVA'::school.estado_inscripcion"
            ),
        ),
    )