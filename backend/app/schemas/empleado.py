from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class EmpleadoCreate(BaseModel):
    nombres: str = Field(
        min_length=1,
        max_length=100,
    )

    apellidos: str = Field(
        min_length=1,
        max_length=100,
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    email: str | None = Field(
        default=None,
        max_length=150,
    )

    cargo: str | None = Field(
        default=None,
        max_length=100,
    )


class EmpleadoUpdate(BaseModel):
    nombres: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    apellidos: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    email: str | None = Field(
        default=None,
        max_length=150,
    )

    cargo: str | None = Field(
        default=None,
        max_length=100,
    )


class EmpleadoEstadoUpdate(BaseModel):
    activo: bool


class EmpleadoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_empleado: int

    nombres: str
    apellidos: str

    telefono: str | None
    email: str | None
    cargo: str | None

    activo: bool
    creado_en: datetime