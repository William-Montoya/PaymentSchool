from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


EstadoEstudiante = Literal[
    "ACTIVO",
    "INACTIVO",
    "RETIRADO",
    "EGRESADO",
]


class EstudianteBase(BaseModel):
    cui: str | None = Field(
        default=None,
        max_length=30,
    )

    nombres: str = Field(
        min_length=1,
        max_length=150,
    )

    apellidos: str = Field(
        min_length=1,
        max_length=150,
    )

    fecha_nacimiento: date | None = None

    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    whatsapp: str | None = Field(
        default=None,
        max_length=30,
    )

    email: EmailStr | None = None

    direccion: str | None = None


class EstudianteCreate(
    EstudianteBase
):
    pass


class EstudianteUpdate(BaseModel):
    cui: str | None = Field(
        default=None,
        max_length=30,
    )

    nombres: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    apellidos: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    fecha_nacimiento: date | None = None

    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    whatsapp: str | None = Field(
        default=None,
        max_length=30,
    )

    email: EmailStr | None = None

    direccion: str | None = None


class EstudianteEstadoUpdate(
    BaseModel
):
    estado: EstadoEstudiante


class EstudianteResponse(
    EstudianteBase
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_estudiante: int

    codigo_estudiante: str = Field(
        min_length=1,
        max_length=50,
    )

    estado: EstadoEstudiante

    creado_en: datetime
    actualizado_en: datetime