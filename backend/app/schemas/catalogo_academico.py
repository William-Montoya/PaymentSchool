from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EstadoCiclo = Literal[
    "PLANIFICADO",
    "ACTIVO",
    "CERRADO",
]


class CicloCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    fecha_inicio: date
    fecha_fin: date
    estado: EstadoCiclo = "PLANIFICADO"


class CicloResponse(CicloCreate):
    model_config = ConfigDict(from_attributes=True)

    id_ciclo: int
    creado_en: datetime


class CarreraCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: str | None = None


class CarreraResponse(CarreraCreate):
    model_config = ConfigDict(from_attributes=True)

    id_carrera: int
    activo: bool
    creado_en: datetime


class CarreraCicloCreate(BaseModel):
    id_carrera: int
    id_ciclo: int
    nombre_comercial: str | None = Field(
        default=None,
        max_length=150,
    )


class CarreraCicloResponse(CarreraCicloCreate):
    model_config = ConfigDict(from_attributes=True)

    id_carrera_ciclo: int
    estado: bool
    creado_en: datetime


class GradoCreate(BaseModel):
    id_carrera_ciclo: int
    nombre: str = Field(min_length=1, max_length=100)
    nivel_orden: int | None = Field(
        default=None,
        gt=0,
    )


class GradoResponse(GradoCreate):
    model_config = ConfigDict(from_attributes=True)

    id_grado: int
    activo: bool