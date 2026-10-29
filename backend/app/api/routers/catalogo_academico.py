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
from app.repositories.catalogo_academico_repository import (
    CatalogoAcademicoRepository,
)
from app.schemas.catalogo_academico import (
    CarreraCicloCreate,
    CarreraCicloResponse,
    CarreraCreate,
    CarreraResponse,
    CicloCreate,
    CicloResponse,
    GradoCreate,
    GradoResponse,
)
from app.services.catalogo_academico_service import (
    CatalogoAcademicoService,
)


router = APIRouter()


# ============================================================
# CICLOS ESCOLARES
# ============================================================

@router.post(
    "/ciclos",
    response_model=CicloResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Ciclos Escolares"],
)
def crear_ciclo(
    data: CicloCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return CatalogoAcademicoService.crear_ciclo(
        db,
        data,
    )


@router.get(
    "/ciclos",
    response_model=list[CicloResponse],
    tags=["Ciclos Escolares"],
)
def listar_ciclos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return CatalogoAcademicoRepository.list_ciclos(
        db
    )


# ============================================================
# CARRERAS
# ============================================================

@router.post(
    "/carreras",
    response_model=CarreraResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Carreras"],
)
def crear_carrera(
    data: CarreraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return CatalogoAcademicoService.crear_carrera(
        db,
        data,
    )


@router.get(
    "/carreras",
    response_model=list[CarreraResponse],
    tags=["Carreras"],
)
def listar_carreras(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return CatalogoAcademicoRepository.list_carreras(
        db
    )


# ============================================================
# CARRERA POR CICLO
# ============================================================

@router.post(
    "/carrera-ciclos",
    response_model=CarreraCicloResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Carrera por Ciclo"],
)
def crear_carrera_ciclo(
    data: CarreraCicloCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return (
        CatalogoAcademicoService
        .crear_carrera_ciclo(
            db,
            data,
        )
    )


@router.get(
    "/carrera-ciclos",
    response_model=list[CarreraCicloResponse],
    tags=["Carrera por Ciclo"],
)
def listar_carrera_ciclos(
    id_ciclo: int | None = Query(
        default=None
    ),
    id_carrera: int | None = Query(
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
        CatalogoAcademicoRepository
        .list_carrera_ciclos(
            db,
            id_ciclo=id_ciclo,
            id_carrera=id_carrera,
        )
    )


# ============================================================
# GRADOS
# ============================================================

@router.post(
    "/grados",
    response_model=GradoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Grados"],
)
def crear_grado(
    data: GradoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_GESTIONAR
        )
    ),
):
    return CatalogoAcademicoService.crear_grado(
        db,
        data,
    )


@router.get(
    "/grados",
    response_model=list[GradoResponse],
    tags=["Grados"],
)
def listar_grados(
    id_carrera_ciclo: int | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            ACADEMICO_VER
        )
    ),
):
    return CatalogoAcademicoRepository.list_grados(
        db,
        id_carrera_ciclo=id_carrera_ciclo,
    )