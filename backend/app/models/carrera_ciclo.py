from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CarreraCiclo(Base):
    __tablename__ = "carrera_ciclo"

    id_carrera_ciclo: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_carrera: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.carrera.id_carrera",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    id_ciclo: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.ciclo_escolar.id_ciclo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    nombre_comercial: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    estado: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true"
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    carrera: Mapped["Carrera"] = relationship(
        "Carrera",
        back_populates="carrera_ciclos",
    )

    ciclo: Mapped["CicloEscolar"] = relationship(
        "CicloEscolar",
        back_populates="carrera_ciclos",
    )

    grados: Mapped[list["Grado"]] = relationship(
        "Grado",
        back_populates="carrera_ciclo",
    )

    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        "Inscripcion",
        back_populates="carrera_ciclo",
    )

    precios: Mapped[list["PrecioCarrera"]] = relationship(
        "PrecioCarrera",
        back_populates="carrera_ciclo",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_carrera",
            "id_ciclo",
            name="uq_carrera_ciclo",
        ),
    )