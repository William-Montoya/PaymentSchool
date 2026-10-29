from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.permiso import (
    PermisoResponse,
)


EstadoUsuario = Literal[
    "ACTIVO",
    "INACTIVO",
    "BLOQUEADO",
]


class UsuarioCreate(BaseModel):
    id_empleado: int

    username: str = Field(
        min_length=3,
        max_length=80,
        pattern=r"^[A-Za-z0-9._-]+$",
    )

    password: str = Field(
        min_length=12,
        max_length=128,
    )

    ids_rol: list[int] = Field(
        min_length=1,
    )


class UsuarioRolesUpdate(BaseModel):
    ids_rol: list[int] = Field(
        min_length=1,
    )


class UsuarioEstadoUpdate(BaseModel):
    estado: EstadoUsuario


class UsuarioPasswordUpdate(BaseModel):
    nueva_password: str = Field(
        min_length=12,
        max_length=128,
    )


class UsuarioRolResponse(BaseModel):
    id_rol: int
    nombre: str
    descripcion: str | None
    activo: bool


class UsuarioDetalleResponse(BaseModel):
    id_usuario: int

    id_empleado: int | None
    empleado: str | None
    cargo: str | None

    username: str
    estado: EstadoUsuario

    ultimo_acceso: datetime | None
    creado_en: datetime

    roles: list[UsuarioRolResponse]
    permisos: list[PermisoResponse]