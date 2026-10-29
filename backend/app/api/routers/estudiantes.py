from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    ESTUDIANTES_GESTIONAR,
    ESTUDIANTES_VER,
)
from app.models.usuario import Usuario
from app.schemas.estudiante import (
    EstudianteCreate,
    EstudianteEstadoUpdate,
    EstudianteResponse,
    EstudianteUpdate,
)
from app.services.estudiante_service import EstudianteService


router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"],
)


@router.post(
    "",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_estudiante(
    data: EstudianteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ESTUDIANTES_GESTIONAR
        )
    ),
):
    return EstudianteService.crear(
        db,
        data,
    )


@router.get(
    "",
    response_model=list[EstudianteResponse],
)
def listar_estudiantes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    estado: str | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ESTUDIANTES_VER
        )
    ),
):
    return EstudianteService.listar(
        db=db,
        offset=offset,
        limit=limit,
        estado=estado,
        buscar=buscar,
    )


@router.get(
    "/{id_estudiante}",
    response_model=EstudianteResponse,
)
def obtener_estudiante(
    id_estudiante: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ESTUDIANTES_VER
        )
    ),
):
    return EstudianteService.obtener(
        db,
        id_estudiante,
    )


@router.put(
    "/{id_estudiante}",
    response_model=EstudianteResponse,
)
def actualizar_estudiante(
    id_estudiante: int,
    data: EstudianteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ESTUDIANTES_GESTIONAR
        )
    ),
):
    return EstudianteService.actualizar(
        db,
        id_estudiante,
        data,
    )


@router.patch(
    "/{id_estudiante}/estado",
    response_model=EstudianteResponse,
)
def cambiar_estado_estudiante(
    id_estudiante: int,
    data: EstudianteEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ESTUDIANTES_GESTIONAR
        )
    ),
):
    return EstudianteService.cambiar_estado(
        db,
        id_estudiante,
        data,
    )