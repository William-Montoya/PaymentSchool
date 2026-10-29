from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Recibo(Base):
    __tablename__ = "recibo"

    id_recibo: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_pago: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "school.pago.id_pago",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_recibo_pago",
        ),
        nullable=False,
    )

    numero_recibo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    codigo_verificacion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    pago: Mapped["Pago"] = relationship(
        "Pago",
        back_populates="recibo",
        uselist=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "id_pago",
            name="uq_recibo_pago",
        ),
        UniqueConstraint(
            "numero_recibo",
            name="uq_recibo_numero",
        ),
        UniqueConstraint(
            "codigo_verificacion",
            name="uq_recibo_codigo",
        ),
    )