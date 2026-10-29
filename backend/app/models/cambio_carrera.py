from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CambioCarrera(Base):
    __tablename__ = "cambio_carrera"

    id_cambio: Mapped[int] = mapped_column(
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
            name="fk_cambio_estudiante",
        ),
        nullable=False,
    )

    id_inscripcion_origen: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.inscripcion.id_inscripcion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_cambio_inscripcion_origen",
        ),
        nullable=False,
    )

    id_inscripcion_destino: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.inscripcion.id_inscripcion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_cambio_inscripcion_destino",
        ),
        nullable=True,
    )

    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    fecha_aprobacion: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp()
    )

    motivo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "SOLICITADO",
            "APROBADO",
            "RECHAZADO",
            "CANCELADO",
            name="estado_cambio_carrera",
            schema="school",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
        server_default="SOLICITADO",
    )

    id_usuario: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante",
        back_populates="cambios_carrera",
    )

    inscripcion_origen: Mapped["Inscripcion"] = relationship(
        "Inscripcion",
        foreign_keys=[id_inscripcion_origen],
        back_populates="cambios_carrera_origen",
    )

    inscripcion_destino: Mapped["Inscripcion | None"] = relationship(
        "Inscripcion",
        foreign_keys=[id_inscripcion_destino],
        back_populates="cambios_carrera_destino",
    )