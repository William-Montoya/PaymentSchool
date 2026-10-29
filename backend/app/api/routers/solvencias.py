from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    FINANZAS_VER,
    SOLVENCIAS_GENERAR,
)
from app.models.usuario import Usuario
from app.repositories.solvencia_repository import (
    SolvenciaRepository,
)
from app.schemas.solvencia import (
    EstadoSolvencia,
    SolvenciaDetalleResponse,
    SolvenciaGenerarCreate,
)
from app.services.solvencia_service import (
    SolvenciaService,
)


router = APIRouter(
    prefix="/solvencias",
    tags=["Solvencias"],
)


@router.post(
    "/generar",
    response_model=SolvenciaDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def generar_solvencia(
    data: SolvenciaGenerarCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SOLVENCIAS_GENERAR
        )
    ),
):
    return SolvenciaService.generar(
        db,
        data,
        current_user.id_usuario,
    )


@router.get(
    "",
    response_model=list[SolvenciaDetalleResponse],
)
def listar_solvencias(
    id_estudiante: int | None = Query(default=None),
    id_evaluacion: int | None = Query(default=None),
    estado: EstadoSolvencia | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return SolvenciaRepository.list(
        db=db,
        id_estudiante=id_estudiante,
        id_evaluacion=id_evaluacion,
        estado=estado,
    )


@router.get(
    "/verificar/{codigo}",
    response_model=SolvenciaDetalleResponse,
)
def verificar_solvencia(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return SolvenciaService.verificar(
        db,
        codigo,
    )


@router.get(
    "/{id_solvencia}",
    response_model=SolvenciaDetalleResponse,
)
def obtener_solvencia(
    id_solvencia: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return SolvenciaService.obtener(
        db,
        id_solvencia,
    )