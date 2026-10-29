from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    SEGURIDAD_GESTIONAR,
    SEGURIDAD_VER,
)
from app.models.usuario import Usuario
from app.repositories.permiso_repository import (
    PermisoRepository,
)
from app.schemas.permiso import (
    PermisoCreate,
    PermisoResponse,
    PermisoUpdate,
)
from app.services.permiso_service import (
    PermisoService,
)


router = APIRouter(
    prefix="/permisos",
    tags=["Seguridad - Permisos"],
)


# ============================================================
# CREAR
# ============================================================

@router.post(
    "",
    response_model=PermisoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    data: PermisoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return PermisoService.crear(
        db,
        data,
        current_user.id_usuario,
    )


# ============================================================
# LISTAR
# ============================================================

@router.get(
    "",
    response_model=list[PermisoResponse],
)
def listar(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_VER
        )
    ),
):
    return PermisoRepository.list(
        db
    )


# ============================================================
# ACTUALIZAR
# ============================================================

@router.patch(
    "/{id_permiso}",
    response_model=PermisoResponse,
)
def actualizar(
    id_permiso: int,
    data: PermisoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return PermisoService.actualizar(
        db,
        id_permiso,
        data,
        current_user.id_usuario,
    )