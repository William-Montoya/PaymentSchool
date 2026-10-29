from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


TipoMovimientoSaldo = Literal[
    "TRASLADO_SALDO",
    "AJUSTE",
    "DEVOLUCION",
    "COMPENSACION",
]

EstadoMovimientoSaldo = Literal[
    "PENDIENTE",
    "APLICADO",
    "ANULADO",
]


class TrasladoSaldoCreate(BaseModel):
    id_estudiante: int

    id_inscripcion_origen: int
    id_inscripcion_destino: int

    monto: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    motivo: str = Field(
        min_length=3,
        max_length=1000,
    )

    referencia: str | None = None


class MovimientoSaldoResponse(BaseModel):
    id_movimiento: int

    id_estudiante: int

    codigo_estudiante: str
    estudiante: str

    id_inscripcion_origen: int | None
    id_inscripcion_destino: int | None

    carrera_origen: str | None
    carrera_destino: str | None

    grado_origen: str | None
    grado_destino: str | None

    tipo: TipoMovimientoSaldo

    monto: Decimal
    fecha_movimiento: datetime

    motivo: str | None

    estado: EstadoMovimientoSaldo

    id_usuario: int | None
    referencia: str | None