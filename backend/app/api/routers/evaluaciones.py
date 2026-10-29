from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    ACADEMICO_GESTIONAR,
    ACADEMICO_VER,
)
from app.models.usuario import Usuario
from app.repositories.evaluacion_repository import (
    EvaluacionRepository,
)
from app.schemas.evaluacion import (
    EvaluacionCreate,
    EvaluacionDetalleResponse,
    EvaluacionEstadoUpdate,
    EvaluacionResponse,
)
from app.services.evaluacion_service import (
    EvaluacionService,
)


router = APIRouter(
    prefix="/evaluaciones",
    tags=["Evaluaciones"],
)


# ============================================================
# CREAR
# ============================================================

@router.post(
    "",
    response_model=EvaluacionResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_evaluacion(
    data: EvaluacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return EvaluacionService.crear(
        db,
        data,
    )


# ============================================================
# LISTAR
# ============================================================

@router.get(
    "",
    response_model=list[
        EvaluacionDetalleResponse
    ],
)
def listar_evaluaciones(
    id_ciclo: int | None = Query(
        default=None
    ),
    activo: bool | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return EvaluacionRepository.list_detalle(
        db=db,
        id_ciclo=id_ciclo,
        activo=activo,
    )


# ============================================================
# OBTENER
# ============================================================

@router.get(
    "/{id_evaluacion}",
    response_model=EvaluacionResponse,
)
def obtener_evaluacion(
    id_evaluacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return EvaluacionService.obtener(
        db,
        id_evaluacion,
    )


# ============================================================
# CAMBIAR ESTADO
# ============================================================

@router.patch(
    "/{id_evaluacion}/estado",
    response_model=EvaluacionResponse,
)
def cambiar_estado_evaluacion(
    id_evaluacion: int,
    data: EvaluacionEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return EvaluacionService.cambiar_estado(
        db,
        id_evaluacion,
        data,
    )