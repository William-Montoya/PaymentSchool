from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


EstadoSolvencia = Literal[
    "SOLVENTE",
    "INSOLVENTE",
]


class SolvenciaGenerarCreate(BaseModel):
    id_estudiante: int
    id_inscripcion: int
    id_evaluacion: int


class SolvenciaResponse(BaseModel):
    id_solvencia: int

    id_estudiante: int
    id_inscripcion: int
    id_evaluacion: int

    fecha_generacion: datetime
    fecha_corte: date

    saldo_corte: Decimal
    estado: EstadoSolvencia

    codigo_verificacion: str

    observaciones: str | None


class SolvenciaDetalleResponse(SolvenciaResponse):
    codigo_estudiante: str
    estudiante: str

    evaluacion: str
    ciclo: str

    carrera: str
    grado: str