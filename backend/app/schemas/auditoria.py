from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditoriaResponse(BaseModel):
    id_auditoria: int

    id_usuario: int | None
    username: str | None

    fecha_evento: datetime

    modulo: str | None
    accion: str | None

    tabla_afectada: str | None
    id_registro: int | None

    descripcion: str | None

    datos_anteriores: dict[str, Any] | None
    datos_nuevos: dict[str, Any] | None

    ip: str | None


class AuditoriaUsuarioFiltro(BaseModel):
    id_usuario: int
    username: str


class AuditoriaCatalogosResponse(BaseModel):
    usuarios: list[AuditoriaUsuarioFiltro]
    modulos: list[str]
    acciones: list[str]
    tablas: list[str]
