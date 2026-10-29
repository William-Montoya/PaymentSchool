from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    EXPEDIENTES_GESTIONAR,
    EXPEDIENTES_VER,
)
from app.models.usuario import Usuario
from app.schemas.expediente import (
    ExpedienteCreate,
    ExpedienteDetalleResponse,
    ExpedienteUpdate,
)
from app.services.expediente_service import (
    ExpedienteService,
)


router = APIRouter(
    prefix="/expedientes",
    tags=["Expedientes"],
)


@router.post(
    "",
    response_model=ExpedienteDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    data: ExpedienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return ExpedienteService.crear(
        db,
        data,
    )


@router.get(
    "/{id_expediente}",
    response_model=ExpedienteDetalleResponse,
)
def obtener(
    id_expediente: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_VER
        )
    ),
):
    return ExpedienteService.obtener(
        db,
        id_expediente,
    )


@router.get(
    "/estudiante/{id_estudiante}",
    response_model=ExpedienteDetalleResponse,
)
def por_estudiante(
    id_estudiante: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_VER
        )
    ),
):
    return (
        ExpedienteService
        .obtener_por_estudiante(
            db,
            id_estudiante,
        )
    )


@router.patch(
    "/{id_expediente}",
    response_model=ExpedienteDetalleResponse,
)
def actualizar(
    id_expediente: int,
    data: ExpedienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return ExpedienteService.actualizar(
        db,
        id_expediente,
        data,
    )