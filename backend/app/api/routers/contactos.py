from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    EXPEDIENTES_GESTIONAR,
    EXPEDIENTES_VER,
)
from app.models.usuario import Usuario
from app.repositories.contacto_repository import (
    ContactoRepository,
)
from app.schemas.contacto import (
    ContactoCreate,
    ContactoEstadoUpdate,
    ContactoResponse,
    ContactoUpdate,
)
from app.services.contacto_service import (
    ContactoService,
)


router = APIRouter(
    prefix="/contactos",
    tags=["Contactos"],
)


@router.post(
    "",
    response_model=ContactoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    data: ContactoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return ContactoService.crear(
        db,
        data,
    )


@router.get(
    "/estudiante/{id_estudiante}",
    response_model=list[ContactoResponse],
)
def listar_estudiante(
    id_estudiante: int,
    activo: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_VER
        )
    ),
):
    return (
        ContactoRepository
        .list_by_estudiante(
            db=db,
            id_estudiante=id_estudiante,
            activo=activo,
        )
    )


@router.put(
    "/{id_contacto}",
    response_model=ContactoResponse,
)
def actualizar(
    id_contacto: int,
    data: ContactoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return ContactoService.actualizar(
        db,
        id_contacto,
        data,
    )


@router.patch(
    "/{id_contacto}/estado",
    response_model=ContactoResponse,
)
def cambiar_estado(
    id_contacto: int,
    data: ContactoEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return ContactoService.cambiar_estado(
        db,
        id_contacto,
        data,
    )