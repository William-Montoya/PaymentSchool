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
    NOTIFICACIONES_GESTIONAR,
    NOTIFICACIONES_VER,
)
from app.models.usuario import Usuario
from app.repositories.notificacion_repository import (
    NotificacionRepository,
)
from app.schemas.notificacion import (
    EstadoDestinatario,
    NotificacionContactoResponse,
    NotificacionCreate,
    NotificacionDeudaCreate,
    NotificacionDeudaResponse,
    NotificacionDestinatarioResponse,
    NotificacionDetalleResponse,
    NotificacionResumenResponse,
)
from app.services.notificacion_service import (
    NotificacionService,
)


router = APIRouter(
    prefix="/notificaciones",
    tags=["Notificaciones"],
)


# ============================================================
# CONTACTOS DISPONIBLES PARA NOTIFICACIONES
# ============================================================

@router.get(
    "/contactos",
    response_model=list[
        NotificacionContactoResponse
    ],
)
def buscar_contactos_notificacion(
    buscar: str | None = Query(
        default=None,
        max_length=150,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            NOTIFICACIONES_GESTIONAR
        )
    ),
):
    return (
        NotificacionService
        .buscar_contactos(
            db=db,
            buscar=buscar,
            limit=limit,
        )
    )


# ============================================================
# CREAR NOTIFICACIÓN
# ============================================================

@router.post(
    "",
    response_model=NotificacionDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_notificacion(
    data: NotificacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            NOTIFICACIONES_GESTIONAR
        )
    ),
):
    return NotificacionService.crear(
        db,
        data,
        current_user.id_usuario,
    )


# ============================================================
# GENERAR AVISO POR DEUDA
# ============================================================

@router.post(
    "/deuda/{id_estudiante}",
    response_model=NotificacionDeudaResponse,
    status_code=status.HTTP_201_CREATED,
)
def generar_aviso_deuda(
    id_estudiante: int,
    data: NotificacionDeudaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            NOTIFICACIONES_GESTIONAR
        )
    ),
):
    return (
        NotificacionService
        .generar_aviso_deuda(
            db,
            id_estudiante,
            data,
            current_user.id_usuario,
        )
    )


# ============================================================
# LISTAR NOTIFICACIONES
# ============================================================

@router.get(
    "",
    response_model=list[
        NotificacionResumenResponse
    ],
)
def listar_notificaciones(
    id_estudiante: int | None = Query(
        default=None
    ),
    estado_destinatario:
        EstadoDestinatario | None = Query(
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
            NOTIFICACIONES_VER
        )
    ),
):
    return (
        NotificacionRepository
        .list(
            db=db,
            id_estudiante=id_estudiante,
            estado_destinatario=
                estado_destinatario,
            offset=offset,
            limit=limit,
        )
    )


# ============================================================
# MARCAR DESTINATARIO COMO ABIERTO
# ============================================================

@router.patch(
    "/destinatarios/"
    "{id_destinatario}/abrir",
    response_model=
        NotificacionDestinatarioResponse,
)
def abrir_notificacion(
    id_destinatario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            NOTIFICACIONES_GESTIONAR
        )
    ),
):
    return (
        NotificacionService
        .marcar_abierto(
            db,
            id_destinatario,
            current_user.id_usuario,
        )
    )


# ============================================================
# OBTENER NOTIFICACIÓN
# ============================================================

@router.get(
    "/{id_notificacion}",
    response_model=
        NotificacionDetalleResponse,
)
def obtener_notificacion(
    id_notificacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            NOTIFICACIONES_VER
        )
    ),
):
    return NotificacionService.obtener(
        db,
        id_notificacion,
    )