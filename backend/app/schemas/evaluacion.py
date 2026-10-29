from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EvaluacionCreate(BaseModel):
    id_ciclo: int

    nombre: str = Field(
        min_length=1,
        max_length=150,
    )

    fecha_evaluacion: date
    fecha_corte_finanzas: date


class EvaluacionEstadoUpdate(BaseModel):
    activo: bool


class EvaluacionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_evaluacion: int
    id_ciclo: int

    nombre: str

    fecha_evaluacion: date
    fecha_corte_finanzas: date

    activo: bool


class EvaluacionDetalleResponse(EvaluacionResponse):
    ciclo: str