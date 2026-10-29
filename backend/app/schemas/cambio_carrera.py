from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EstadoCambioCarrera = Literal[
    "SOLICITADO",
    "APROBADO",
    "RECHAZADO",
    "CANCELADO",
]


class CambioCarreraCreate(BaseModel):
    id_estudiante: int
    id_inscripcion_origen: int

    id_carrera_ciclo_destino: int
    id_grado_destino: int

    motivo: str = Field(
        min_length=3,
        max_length=1000,
    )

    observaciones: str | None = None


class CambioCarreraDetalleResponse(BaseModel):
    id_cambio: int

    id_estudiante: int
    codigo_estudiante: str
    estudiante: str

    id_inscripcion_origen: int
    id_inscripcion_destino: int | None

    id_carrera_ciclo_origen: int
    id_carrera_ciclo_destino: int | None

    carrera_origen: str
    carrera_destino: str | None

    grado_origen: str
    grado_destino: str | None

    ciclo: str

    estado_inscripcion_origen: str
    estado_inscripcion_destino: str | None

    fecha_solicitud: datetime
    fecha_aprobacion: datetime | None

    motivo: str | None
    estado: EstadoCambioCarrera

    id_usuario: int | None
    observaciones: str | None