from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    BECAS_GESTIONAR,
    FINANZAS_VER,
)
from app.models.usuario import Usuario
from app.repositories.beca_repository import (
    BecaRepository,
)
from app.schemas.beca import (
    BecaAplicacionResponse,
    BecaCreate,
    BecaEstadoUpdate,
    BecaEstudianteCreate,
    BecaEstudianteFinalizar,
    BecaEstudianteResponse,
    BecaResponse,
    EstadoBeca,
)
from app.services.beca_service import (
    BecaService,
)


router = APIRouter(
    prefix="/becas",
    tags=["Becas"],
)


@router.post(
    "",
    response_model=BecaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_beca(
    data: BecaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            BECAS_GESTIONAR
        )
    ),
):
    return BecaService.crear(
        db,
        data,
        current_user.id_usuario,
    )


@router.get(
    "",
    response_model=list[BecaResponse],
)
def listar_becas(
    estado: EstadoBeca | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return BecaService.listar(
        db,
        estado,
    )


@router.patch(
    "/{id_beca}/estado",
    response_model=BecaResponse,
)
def cambiar_estado_beca(
    id_beca: int,
    data: BecaEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            BECAS_GESTIONAR
        )
    ),
):
    return BecaService.cambiar_estado(
        db,
        id_beca,
        data,
        current_user.id_usuario,
    )


@router.post(
    "/asignaciones",
    response_model=BecaEstudianteResponse,
    status_code=status.HTTP_201_CREATED,
)
def asignar_beca(
    data: BecaEstudianteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            BECAS_GESTIONAR
        )
    ),
):
    return BecaService.asignar(
        db,
        data,
        current_user.id_usuario,
    )


@router.get(
    "/asignaciones",
    response_model=list[BecaEstudianteResponse],
)
def listar_asignaciones(
    id_estudiante: int | None = Query(
        default=None
    ),
    id_beca: int | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return BecaRepository.list_asignaciones(
        db=db,
        id_estudiante=id_estudiante,
        id_beca=id_beca,
    )


@router.patch(
    "/asignaciones/{id_beca_estudiante}/finalizar",
    response_model=BecaEstudianteResponse,
)
def finalizar_beca_estudiante(
    id_beca_estudiante: int,
    data: BecaEstudianteFinalizar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            BECAS_GESTIONAR
        )
    ),
):
    return BecaService.finalizar_asignacion(
        db,
        id_beca_estudiante,
        data,
        current_user.id_usuario,
    )


@router.post(
    "/asignaciones/{id_beca_estudiante}"
    "/aplicar/{id_obligacion}",
    response_model=BecaAplicacionResponse,
)
def aplicar_beca(
    id_beca_estudiante: int,
    id_obligacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            BECAS_GESTIONAR
        )
    ),
):
    return BecaService.aplicar_a_obligacion(
        db,
        id_beca_estudiante,
        id_obligacion,
        current_user.id_usuario,
    )