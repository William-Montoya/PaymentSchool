from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DocumentoEntregaUpdate(BaseModel):
    entregado: bool


class DocumentoExpedienteResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_documento: int
    id_expediente: int
    id_tipo_documento: int

    nombre_archivo: str | None

    entregado: bool

    fecha_entrega: (
        datetime
        | date
        | None
    )