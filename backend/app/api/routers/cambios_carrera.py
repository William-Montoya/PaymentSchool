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
from app.repositories.cambio_carrera_repository import (
    CambioCarreraRepository,
)
from app.schemas.cambio_carrera import (
    CambioCarreraCreate,
    CambioCarreraDetalleResponse,
    EstadoCambioCarrera,
)
from app.services.cambio_carrera_service import (
    CambioCarreraService,
)


router = APIRouter(
    prefix="/cambios-carrera",
    tags=["Cambios de carrera"],
)


# ============================================================
# REALIZAR CAMBIO
# ============================================================

@router.post(
    "",
    response_model=CambioCarreraDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def realizar_cambio(
    data: CambioCarreraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return CambioCarreraService.realizar(
        db,
        data,
        current_user.id_usuario,
    )


# ============================================================
# LISTAR
# ============================================================

@router.get(
    "",
    response_model=list[
        CambioCarreraDetalleResponse
    ],
)
def listar_cambios(
    id_estudiante: int | None = Query(
        default=None
    ),
    estado: EstadoCambioCarrera | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return (
        CambioCarreraRepository
        .list(
            db=db,
            id_estudiante=id_estudiante,
            estado=estado,
        )
    )


# ============================================================
# OBTENER
# ============================================================

@router.get(
    "/{id_cambio}",
    response_model=CambioCarreraDetalleResponse,
)
def obtener_cambio(
    id_cambio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return CambioCarreraService.obtener(
        db,
        id_cambio,
    )