from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EstadoBeca = Literal[
    "PENDIENTE",
    "ACTIVA",
    "FINALIZADA",
    "CANCELADA",
]


class BecaCreate(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=150,
    )

    descripcion: str | None = None

    porcentaje: Decimal = Field(
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
    )

    convenio: str | None = Field(
        default=None,
        max_length=200,
    )

    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class BecaEstadoUpdate(BaseModel):
    estado: EstadoBeca


class BecaResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_beca: int
    nombre: str
    descripcion: str | None

    porcentaje: Decimal
    convenio: str | None

    estado: EstadoBeca

    fecha_inicio: date | None
    fecha_fin: date | None


class BecaEstudianteCreate(BaseModel):
    id_beca: int
    id_estudiante: int

    fecha_inicio: date
    fecha_fin: date | None = None

    porcentaje_aplicado: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
    )

    observaciones: str | None = None


class BecaEstudianteFinalizar(BaseModel):
    fecha_fin: date


class BecaEstudianteResponse(BaseModel):
    id_beca_estudiante: int
    id_beca: int
    id_estudiante: int

    beca: str
    estudiante: str

    porcentaje_beca: Decimal
    porcentaje_aplicado: Decimal | None
    porcentaje_efectivo: Decimal

    fecha_inicio: date
    fecha_fin: date | None

    observaciones: str | None


class BecaAplicacionResponse(BaseModel):
    id_beca_obligacion: int

    id_beca_estudiante: int
    id_obligacion: int

    beca: str
    concepto: str

    porcentaje_aplicado: Decimal
    monto_aplicado: Decimal

    fecha_aplicacion: datetime

    monto_beca: Decimal
    monto_neto: Decimal
    saldo: Decimal