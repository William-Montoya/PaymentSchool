from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TipoObligacion = Literal[
    "INSCRIPCION",
    "MENSUALIDAD",
    "CERTIFICACION",
    "CONSTANCIA",
    "OTRO",
]

TipoObligacionManual = Literal[
    "INSCRIPCION",
    "CERTIFICACION",
    "CONSTANCIA",
    "OTRO",
]

EstadoObligacion = Literal[
    "PENDIENTE",
    "PARCIAL",
    "PAGADA",
    "ANULADA",
]


class ObligacionDesdePrecioCreate(BaseModel):
    id_inscripcion: int
    id_precio: int
    fecha_vencimiento: date


class ObligacionManualCreate(BaseModel):
    id_inscripcion: int

    concepto: str = Field(
        min_length=1,
        max_length=150,
    )

    tipo_obligacion: TipoObligacionManual

    periodo: str | None = Field(
        default=None,
        max_length=20,
    )

    fecha_vencimiento: date | None = None

    monto_bruto: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )


class GenerarMensualidadesCreate(BaseModel):
    id_inscripcion: int
    id_precio: int

    fecha_inicio: date

    cantidad_meses: int = Field(
        ge=1,
        le=24,
    )


class GenerarMensualidadesResponse(BaseModel):
    mensaje: str
    id_inscripcion: int
    id_precio: int
    fecha_inicio: date
    cantidad_meses: int


class ObligacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_obligacion: int
    id_inscripcion: int
    id_precio: int | None

    concepto: str
    periodo: str | None
    fecha_vencimiento: date | None

    monto_bruto: Decimal
    monto_descuento: Decimal
    monto_beca: Decimal
    monto_neto: Decimal

    estado: EstadoObligacion
    tipo_obligacion: TipoObligacion

    creado_en: datetime


class ObligacionSaldoResponse(ObligacionResponse):
    total_pagado: Decimal
    saldo: Decimal