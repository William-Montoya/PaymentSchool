from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint

from app.core.database import Base


class Grado(Base):
    __tablename__ = "grado"

    id_grado: Mapped[int] = mapped_column(
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
        ),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    nivel_orden: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    carrera_ciclo: Mapped["CarreraCiclo"] = relationship(
        "CarreraCiclo",
        back_populates="grados",
    )

    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        "Inscripcion",
        back_populates="grado",
    )

    __table_args__ = (
        CheckConstraint(
            "nivel_orden IS NULL OR nivel_orden > 0",
            name="ck_grado_orden",
        ),
        UniqueConstraint(
            "id_carrera_ciclo",
            "nombre",
            name="uq_grado_carrera_ciclo_nombre",
        ),
    )