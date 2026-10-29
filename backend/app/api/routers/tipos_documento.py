from fastapi import APIRouter, Depends, Query, status
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
from app.repositories.tipo_documento_repository import (
    TipoDocumentoRepository,
)
from app.schemas.tipo_documento import (
    TipoDocumentoCreate,
    TipoDocumentoEstadoUpdate,
    TipoDocumentoResponse,
    TipoDocumentoUpdate,
)
from app.services.tipo_documento_service import (
    TipoDocumentoService,
)


router = APIRouter(
    prefix="/tipos-documento",
    tags=["Tipos de documento"],
)


@router.post(
    "",
    response_model=TipoDocumentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    data: TipoDocumentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return TipoDocumentoService.crear(
        db,
        data,
    )


@router.get(
    "",
    response_model=list[TipoDocumentoResponse],
)
def listar(
    activo: bool | None = Query(default=None),
    obligatorio: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_VER
        )
    ),
):
    return TipoDocumentoRepository.list(
        db=db,
        activo=activo,
        obligatorio=obligatorio,
    )


@router.put(
    "/{id_tipo_documento}",
    response_model=TipoDocumentoResponse,
)
def actualizar(
    id_tipo_documento: int,
    data: TipoDocumentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return TipoDocumentoService.actualizar(
        db,
        id_tipo_documento,
        data,
    )


@router.patch(
    "/{id_tipo_documento}/estado",
    response_model=TipoDocumentoResponse,
)
def estado(
    id_tipo_documento: int,
    data: TipoDocumentoEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return TipoDocumentoService.cambiar_estado(
        db,
        id_tipo_documento,
        data,
    )