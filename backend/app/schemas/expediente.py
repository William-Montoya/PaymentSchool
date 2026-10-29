from datetime import datetime

from pydantic import BaseModel


class ExpedienteCreate(BaseModel):
    id_estudiante: int
    observaciones: str | None = None


class ExpedienteUpdate(BaseModel):
    observaciones: str | None = None


class ExpedienteResponse(BaseModel):
    id_expediente: int
    id_estudiante: int

    observaciones: str | None

    creado_en: datetime
    actualizado_en: datetime


class EstadoDocumentoResponse(BaseModel):
    id_tipo_documento: int

    nombre: str
    obligatorio: bool

    entregado: bool

    id_documento: int | None
    nombre_archivo: str | None


class ExpedienteDetalleResponse(
    ExpedienteResponse
):
    codigo_estudiante: str
    estudiante: str

    documentos_requeridos: int
    documentos_entregados: int
    documentos_pendientes: int

    completo: bool

    documentos: list[EstadoDocumentoResponse]