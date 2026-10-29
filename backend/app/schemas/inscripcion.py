from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


TipoInscripcion = Literal[
    "NUEVA",
    "REINSCRIPCION",
    "TRASLADO",
]

EstadoInscripcion = Literal[
    "ACTIVA",
    "FINALIZADA",
    "CANCELADA",
    "RETIRADA",
]


class InscripcionCreate(BaseModel):
    id_estudiante: int
    id_carrera_ciclo: int
    id_grado: int

    tipo: TipoInscripcion = "NUEVA"
    observaciones: str | None = None


class InscripcionEstadoUpdate(BaseModel):
    estado: EstadoInscripcion


class InscripcionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_inscripcion: int
    id_estudiante: int
    id_carrera_ciclo: int
    id_grado: int

    fecha_inscripcion: date
    tipo: TipoInscripcion
    estado: EstadoInscripcion

    observaciones: str | None
    creado_en: datetime


class InscripcionDetalleResponse(InscripcionResponse):
    codigo_estudiante: str
    estudiante: str

    carrera: str
    ciclo: str
    grado: str