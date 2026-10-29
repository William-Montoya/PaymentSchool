from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


EstadoDestinatario = Literal[
    "GENERADO",
    "ABIERTO",
]


class NotificacionCreate(BaseModel):
    titulo: str = Field(
        min_length=1,
        max_length=200,
    )

    mensaje: str = Field(
        min_length=1,
    )

    ids_contacto: list[int] = Field(
        min_length=1,
        max_length=200,
    )


class NotificacionDeudaCreate(BaseModel):
    # Si viene null:
    # 1. intenta contacto principal activo
    # 2. si no existe, usa otro contacto activo
    id_contacto: int | None = None


class NotificacionContactoResponse(BaseModel):
    id_contacto: int
    id_estudiante: int

    codigo_estudiante: str
    estudiante: str

    contacto: str
    parentesco: str | None

    telefono: str | None
    whatsapp: str | None
    email: str | None

    es_principal: bool


class NotificacionDestinatarioResponse(BaseModel):
    id_destinatario: int
    id_contacto: int

    contacto: str

    id_estudiante: int
    codigo_estudiante: str
    estudiante: str

    telefono: str | None
    whatsapp: str | None
    email: str | None

    es_principal: bool

    estado: EstadoDestinatario

    fecha_generado: datetime
    fecha_abierto: datetime | None


class NotificacionResumenResponse(BaseModel):
    id_notificacion: int

    titulo: str
    mensaje: str

    fecha_creacion: datetime
    id_usuario: int | None

    total_destinatarios: int
    total_abiertos: int
    total_pendientes: int


class NotificacionDetalleResponse(BaseModel):
    id_notificacion: int

    titulo: str
    mensaje: str

    fecha_creacion: datetime
    id_usuario: int | None

    total_destinatarios: int
    total_abiertos: int
    total_pendientes: int

    destinatarios: list[
        NotificacionDestinatarioResponse
    ]


class NotificacionDeudaResponse(
    NotificacionDetalleResponse
):
    deuda_total: Decimal