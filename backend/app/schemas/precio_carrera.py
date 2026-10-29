from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TipoPrecio = Literal[
    "INSCRIPCION",
    "MENSUALIDAD",
    "OTRO",
]


class PrecioCarreraCreate(BaseModel):
    id_carrera_ciclo: int
    id_grado: int

    tipo: TipoPrecio

    concepto: str = Field(
        min_length=1,
        max_length=150,
    )

    monto: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    fecha_inicio: date
    fecha_fin: date | None = None


class PrecioCarreraEstadoUpdate(BaseModel):
    activo: bool


class PrecioCarreraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_precio: int
    id_carrera_ciclo: int
    id_grado: int | None

    tipo: TipoPrecio
    concepto: str
    monto: Decimal

    fecha_inicio: date
    fecha_fin: date | None

    activo: bool
    creado_en: datetime