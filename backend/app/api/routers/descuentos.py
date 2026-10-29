from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    DESCUENTOS_GESTIONAR,
    FINANZAS_VER,
)
from app.models.usuario import Usuario
from app.repositories.descuento_repository import (
    DescuentoRepository,
)
from app.schemas.descuento import (
    DescuentoAplicacionResponse,
    DescuentoCreate,
    DescuentoEstadoUpdate,
    DescuentoResponse,
)
from app.services.descuento_service import (
    DescuentoService,
)


router = APIRouter(
    prefix="/descuentos",
    tags=["Descuentos"],
)


@router.post(
    "",
    response_model=DescuentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_descuento(
    data: DescuentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            DESCUENTOS_GESTIONAR
        )
    ),
):
    return DescuentoService.crear(
        db,
        data,
        current_user.id_usuario,
    )


@router.get(
    "",
    response_model=list[DescuentoResponse],
)
def listar_descuentos(
    activo: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return DescuentoService.listar(
        db,
        activo,
    )


@router.get(
    "/aplicaciones",
    response_model=list[DescuentoAplicacionResponse],
)
def listar_aplicaciones(
    id_obligacion: int | None = Query(
        default=None
    ),
    id_descuento: int | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return (
        DescuentoRepository
        .list_aplicaciones(
            db=db,
            id_obligacion=id_obligacion,
            id_descuento=id_descuento,
        )
    )


@router.patch(
    "/{id_descuento}/estado",
    response_model=DescuentoResponse,
)
def cambiar_estado(
    id_descuento: int,
    data: DescuentoEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            DESCUENTOS_GESTIONAR
        )
    ),
):
    return DescuentoService.cambiar_estado(
        db,
        id_descuento,
        data,
        current_user.id_usuario,
    )


@router.post(
    "/{id_descuento}/aplicar/{id_obligacion}",
    response_model=DescuentoAplicacionResponse,
)
def aplicar_descuento(
    id_descuento: int,
    id_obligacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            DESCUENTOS_GESTIONAR
        )
    ),
):
    return DescuentoService.aplicar(
        db,
        id_descuento,
        id_obligacion,
        current_user.id_usuario,
    )