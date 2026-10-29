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
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.schemas.inscripcion import (
    InscripcionCreate,
    InscripcionDetalleResponse,
    InscripcionEstadoUpdate,
)
from app.services.inscripcion_service import (
    InscripcionService,
)


router = APIRouter(
    prefix="/inscripciones",
    tags=["Inscripciones"],
)


# ============================================================
# CREAR INSCRIPCIÓN
# ============================================================

@router.post(
    "",
    response_model=InscripcionDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_inscripcion(
    data: InscripcionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return InscripcionService.crear(
        db,
        data,
        current_user.id_usuario,
    )


# ============================================================
# LISTAR INSCRIPCIONES
# ============================================================

@router.get(
    "",
    response_model=list[
        InscripcionDetalleResponse
    ],
)
def listar_inscripciones(
    id_estudiante: int | None = Query(
        default=None
    ),
    id_ciclo: int | None = Query(
        default=None
    ),
    id_carrera: int | None = Query(
        default=None
    ),
    estado: str | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return InscripcionRepository.list_detalle(
        db=db,
        id_estudiante=id_estudiante,
        id_ciclo=id_ciclo,
        id_carrera=id_carrera,
        estado=estado,
    )


# ============================================================
# OBTENER INSCRIPCIÓN
# ============================================================

@router.get(
    "/{id_inscripcion}",
    response_model=InscripcionDetalleResponse,
)
def obtener_inscripcion(
    id_inscripcion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return InscripcionService.obtener(
        db,
        id_inscripcion,
    )


# ============================================================
# CAMBIAR ESTADO
# ============================================================

@router.patch(
    "/{id_inscripcion}/estado",
    response_model=InscripcionDetalleResponse,
)
def cambiar_estado_inscripcion(
    id_inscripcion: int,
    data: InscripcionEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return InscripcionService.cambiar_estado(
        db,
        id_inscripcion,
        data,
        current_user.id_usuario,
    )