from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DashboardFinancieroResponse(BaseModel):
    estudiantes_activos: int
    inscripciones_activas: int

    total_pagado: Decimal
    deuda_total: Decimal

    estudiantes_insolventes: int


class DeudaPorGradoResponse(BaseModel):
    id_grado: int
    grado: str

    cantidad_estudiantes: int
    deuda_total: Decimal


class DeudaPorEstudianteResponse(BaseModel):
    id_estudiante: int

    codigo_estudiante: str
    estudiante: str

    grado: str

    deuda_total: Decimal


class EstudianteInsolventeResponse(BaseModel):
    id_estudiante: int

    codigo_estudiante: str
    estudiante: str

    id_inscripcion: int
    grado: str

    deuda_total: Decimal


class EstadoCuentaItemResponse(BaseModel):
    id_estudiante: int

    codigo_estudiante: str
    estudiante: str

    id_inscripcion: int

    carrera: str
    grado: str

    id_obligacion: int

    concepto: str
    periodo: str | None

    fecha_vencimiento: date | None

    total_pagado: Decimal
    saldo: Decimal