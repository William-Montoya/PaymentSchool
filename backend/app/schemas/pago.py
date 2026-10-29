from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MetodoPago = Literal[
    "EFECTIVO",
    "TRANSFERENCIA",
    "DEPOSITO",
    "TARJETA",
    "OTRO",
]

EstadoPago = Literal[
    "PENDIENTE",
    "CONFIRMADO",
    "ANULADO",
]

EstadoSaldoFavor = Literal[
    "ACTIVO",
    "AGOTADO",
    "ANULADO",
]

TipoObligacionPago = Literal[
    "INSCRIPCION",
    "MENSUALIDAD",
    "CERTIFICACION",
    "CONSTANCIA",
    "OTRO",
]


class PagoCreate(BaseModel):
    id_estudiante: int

    monto: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    metodo: MetodoPago

    referencia: str | None = Field(
        default=None,
        max_length=150,
    )

    observaciones: str | None = None


class PagoAutomaticoCreate(PagoCreate):
    pass


class AplicacionPagoCreate(BaseModel):
    id_obligacion: int

    monto: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )


class PagoAnular(BaseModel):
    motivo: str = Field(
        min_length=3,
        max_length=500,
    )


class CobroCreate(BaseModel):
    id_estudiante: int

    id_obligaciones: list[int] = Field(
        min_length=1,
    )

    monto: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    metodo: MetodoPago

    referencia: str | None = Field(
        default=None,
        max_length=150,
    )

    observaciones: str | None = None


class PagoResponse(BaseModel):
    id_pago: int
    id_estudiante: int
    id_usuario: int | None

    fecha_pago: datetime
    monto_total: Decimal

    metodo: MetodoPago
    referencia: str | None
    observaciones: str | None

    estado: EstadoPago
    creado_en: datetime

    total_aplicado: Decimal
    saldo_disponible: Decimal | None


class AplicacionPagoResponse(BaseModel):
    id_aplicacion: int
    id_pago: int
    id_obligacion: int

    concepto: str
    periodo: str | None

    monto_aplicado: Decimal
    fecha_aplicacion: datetime


class AplicacionDetallePagoResponse(AplicacionPagoResponse):
    tipo_obligacion: TipoObligacionPago
    fecha_vencimiento: date | None
    monto_obligacion: Decimal


class SaldoFavorResponse(BaseModel):
    id_saldo_favor: int
    id_estudiante: int
    id_pago_origen: int | None

    monto_original: Decimal
    monto_disponible: Decimal

    fecha_generacion: datetime
    estado: EstadoSaldoFavor

    observaciones: str | None


class AplicarSaldoFavorCreate(BaseModel):
    id_obligacion: int

    monto: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )


class AplicarSaldoFavorResponse(BaseModel):
    mensaje: str

    id_saldo_favor: int
    id_obligacion: int

    monto_aplicado: Decimal
    monto_disponible: Decimal

    estado: EstadoSaldoFavor


class ReciboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_recibo: int
    id_pago: int

    numero_recibo: str
    codigo_verificacion: str

    fecha_emision: datetime


class PagoAutomaticoResponse(BaseModel):
    pago: PagoResponse
    saldo_favor: SaldoFavorResponse | None


class CobroResponse(BaseModel):
    pago: PagoResponse
    recibo: ReciboResponse
    aplicaciones: list[AplicacionDetallePagoResponse]
    total_seleccionado: Decimal
    total_aplicado: Decimal
    saldo_seleccionado_restante: Decimal


class ComprobantePagoResponse(BaseModel):
    pago: PagoResponse
    recibo: ReciboResponse | None
    aplicaciones: list[AplicacionDetallePagoResponse]
