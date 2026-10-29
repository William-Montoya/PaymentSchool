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
from app.schemas.usuario import (
    EstadoUsuario,
    UsuarioCreate,
    UsuarioDetalleResponse,
    UsuarioEstadoUpdate,
    UsuarioPasswordUpdate,
    UsuarioRolesUpdate,
)
from app.services.usuario_service import (
    UsuarioService,
)


router = APIRouter(
    prefix="/usuarios",
    tags=["Seguridad - Usuarios"],
)


# ============================================================
# CREAR
# ============================================================

@router.post(
    "",
    response_model=UsuarioDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return UsuarioService.crear(
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
        UsuarioDetalleResponse
    ],
)
def listar(
    estado: EstadoUsuario | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_VER
        )
    ),
):
    return UsuarioService.listar(
        db,
        estado,
    )


# ============================================================
# OBTENER
# ============================================================

@router.get(
    "/{id_usuario}",
    response_model=UsuarioDetalleResponse,
)
def obtener(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_VER
        )
    ),
):
    return UsuarioService.obtener(
        db,
        id_usuario,
    )


# ============================================================
# ASIGNAR / REEMPLAZAR ROLES
# ============================================================

@router.put(
    "/{id_usuario}/roles",
    response_model=UsuarioDetalleResponse,
)
def asignar_roles(
    id_usuario: int,
    data: UsuarioRolesUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return UsuarioService.asignar_roles(
        db,
        id_usuario,
        data,
        current_user.id_usuario,
    )


# ============================================================
# CAMBIAR ESTADO
# ============================================================

@router.patch(
    "/{id_usuario}/estado",
    response_model=UsuarioDetalleResponse,
)
def cambiar_estado(
    id_usuario: int,
    data: UsuarioEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return UsuarioService.cambiar_estado(
        db,
        id_usuario,
        data,
        current_user.id_usuario,
    )


# ============================================================
# CAMBIAR PASSWORD
# ============================================================

@router.patch(
    "/{id_usuario}/password",
    response_model=UsuarioDetalleResponse,
)
def cambiar_password(
    id_usuario: int,
    data: UsuarioPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SEGURIDAD_GESTIONAR
        )
    ),
):
    return UsuarioService.cambiar_password(
        db,
        id_usuario,
        data,
        current_user.id_usuario,
    )