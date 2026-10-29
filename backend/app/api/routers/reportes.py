from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    REPORTES_VER,
)
from app.models.usuario import Usuario
from app.schemas.reporte import (
    DashboardFinancieroResponse,
    DeudaPorEstudianteResponse,
    DeudaPorGradoResponse,
    EstadoCuentaItemResponse,
    EstudianteInsolventeResponse,
)
from app.services.reporte_service import (
    ReporteService,
)


router = APIRouter(
    prefix="/reportes",
    tags=["Reportes y Dashboard"],
)


# ============================================================
# DASHBOARD FINANCIERO
# ============================================================

@router.get(
    "/dashboard",
    response_model=DashboardFinancieroResponse,
)
def dashboard_financiero(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            REPORTES_VER
        )
    ),
):
    return ReporteService.dashboard(
        db
    )


# ============================================================
# DEUDA POR GRADO
# ============================================================

@router.get(
    "/deuda-por-grado",
    response_model=list[DeudaPorGradoResponse],
)
def deuda_por_grado(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            REPORTES_VER
        )
    ),
):
    return ReporteService.deuda_por_grado(
        db
    )


# ============================================================
# DEUDA POR ESTUDIANTE
# ============================================================

@router.get(
    "/deuda-por-estudiante",
    response_model=list[
        DeudaPorEstudianteResponse
    ],
)
def deuda_por_estudiante(
    buscar: str | None = Query(
        default=None,
        max_length=150,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            REPORTES_VER
        )
    ),
):
    return (
        ReporteService
        .deuda_por_estudiante(
            db=db,
            buscar=buscar,
            offset=offset,
            limit=limit,
        )
    )


# ============================================================
# ESTUDIANTES INSOLVENTES
# ============================================================

@router.get(
    "/estudiantes-insolventes",
    response_model=list[
        EstudianteInsolventeResponse
    ],
)
def estudiantes_insolventes(
    buscar: str | None = Query(
        default=None,
        max_length=150,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            REPORTES_VER
        )
    ),
):
    return (
        ReporteService
        .estudiantes_insolventes(
            db=db,
            buscar=buscar,
            offset=offset,
            limit=limit,
        )
    )


# ============================================================
# ESTADO DE CUENTA
# ============================================================

@router.get(
    "/estado-cuenta/{id_estudiante}",
    response_model=list[
        EstadoCuentaItemResponse
    ],
)
def estado_cuenta_estudiante(
    id_estudiante: int,
    id_inscripcion: int | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            REPORTES_VER
        )
    ),
):
    return ReporteService.estado_cuenta(
        db=db,
        id_estudiante=id_estudiante,
        id_inscripcion=id_inscripcion,
    )