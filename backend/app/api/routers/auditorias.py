from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    AUDITORIA_VER,
)
from app.models.usuario import Usuario
from app.schemas.auditoria import (
    AuditoriaCatalogosResponse,
    AuditoriaResponse,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoria"],
)


@router.get(
    "/catalogos",
    response_model=AuditoriaCatalogosResponse,
)
def catalogos_auditoria(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            AUDITORIA_VER
        )
    ),
):
    return AuditoriaService.catalogos(
        db
    )


@router.get(
    "",
    response_model=list[AuditoriaResponse],
)
def listar_auditoria(
    id_usuario: int | None = Query(
        default=None,
        ge=1,
    ),
    modulo: str | None = Query(
        default=None,
        max_length=100,
    ),
    accion: str | None = Query(
        default=None,
        max_length=100,
    ),
    tabla_afectada: str | None = Query(
        default=None,
        max_length=100,
    ),
    id_registro: int | None = Query(
        default=None,
        ge=1,
    ),
    fecha_desde: datetime | None = Query(
        default=None
    ),
    fecha_hasta: datetime | None = Query(
        default=None
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
            AUDITORIA_VER
        )
    ),
):
    return AuditoriaService.listar(
        db=db,
        id_usuario=id_usuario,
        modulo=modulo,
        accion=accion,
        tabla_afectada=tabla_afectada,
        id_registro=id_registro,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{id_auditoria}",
    response_model=AuditoriaResponse,
)
def obtener_auditoria(
    id_auditoria: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            AUDITORIA_VER
        )
    ),
):
    return AuditoriaService.obtener(
        db,
        id_auditoria,
    )
