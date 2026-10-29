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
from app.repositories.empleado_repository import (
    EmpleadoRepository,
)
from app.schemas.empleado import (
    EmpleadoCreate,
    EmpleadoEstadoUpdate,
    EmpleadoResponse,
    EmpleadoUpdate,
)
from app.services.empleado_service import (
    EmpleadoService,
)


router = APIRouter(
    prefix="/empleados",
    tags=["Seguridad - Empleados"],
)


# ============================================================
# CREAR
# ============================================================

@router.post(
    "",
    response_model=EmpleadoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    data: EmpleadoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return EmpleadoService.crear(
        db,
        data,
    )


# ============================================================
# LISTAR
# ============================================================

@router.get(
    "",
    response_model=list[EmpleadoResponse],
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
    return EmpleadoRepository.list(
        db,
        activo,
    )


# ============================================================
# OBTENER
# ============================================================

@router.get(
    "/{id_empleado}",
    response_model=EmpleadoResponse,
)
def obtener(
    id_empleado: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_VER
        )
    ),
):
    return EmpleadoService.obtener(
        db,
        id_empleado,
    )


# ============================================================
# ACTUALIZAR
# ============================================================

@router.put(
    "/{id_empleado}",
    response_model=EmpleadoResponse,
)
def actualizar(
    id_empleado: int,
    data: EmpleadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return EmpleadoService.actualizar(
        db,
        id_empleado,
        data,
    )


# ============================================================
# CAMBIAR ESTADO
# ============================================================

@router.patch(
    "/{id_empleado}/estado",
    response_model=EmpleadoResponse,
)
def cambiar_estado(
    id_empleado: int,
    data: EmpleadoEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return EmpleadoService.cambiar_estado(
        db,
        id_empleado,
        data,
    )