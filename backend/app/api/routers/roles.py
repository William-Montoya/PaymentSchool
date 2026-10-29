from fastapi import (
    APIRouter,
    Depends,
    Query,
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
from app.repositories.rol_repository import (
    RolRepository,
)
from app.schemas.rol import (
    RolCreate,
    RolDetalleResponse,
    RolEstadoUpdate,
    RolPermisosUpdate,
    RolUpdate,
)
from app.services.rol_service import (
    RolService,
)


router = APIRouter(
    prefix="/roles",
    tags=["Seguridad - Roles"],
)


# ============================================================
# CREAR
# ============================================================

@router.post(
    "",
    response_model=RolDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    data: RolCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return RolService.crear(
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
        RolDetalleResponse
    ],
)
def listar(
    activo: bool | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_VER
        )
    ),
):
    roles = RolRepository.list(
        db,
        activo,
    )

    return [
        RolService.obtener(
            db,
            rol.id_rol,
        )
        for rol in roles
    ]


# ============================================================
# OBTENER
# ============================================================

@router.get(
    "/{id_rol}",
    response_model=RolDetalleResponse,
)
def obtener(
    id_rol: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_VER
        )
    ),
):
    return RolService.obtener(
        db,
        id_rol,
    )


# ============================================================
# ACTUALIZAR
# ============================================================

@router.patch(
    "/{id_rol}",
    response_model=RolDetalleResponse,
)
def actualizar(
    id_rol: int,
    data: RolUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return RolService.actualizar(
        db,
        id_rol,
        data,
        current_user.id_usuario,
    )


# ============================================================
# CAMBIAR ESTADO
# ============================================================

@router.patch(
    "/{id_rol}/estado",
    response_model=RolDetalleResponse,
)
def cambiar_estado(
    id_rol: int,
    data: RolEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return RolService.cambiar_estado(
        db,
        id_rol,
        data,
        current_user.id_usuario,
    )


# ============================================================
# ASIGNAR / REEMPLAZAR PERMISOS
# ============================================================

@router.put(
    "/{id_rol}/permisos",
    response_model=RolDetalleResponse,
)
def asignar_permisos(
    id_rol: int,
    data: RolPermisosUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return RolService.asignar_permisos(
        db,
        id_rol,
        data,
        current_user.id_usuario,
    )