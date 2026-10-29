from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    FINANZAS_VER,
    PRECIOS_GESTIONAR,
)
from app.models.usuario import Usuario
from app.schemas.precio_carrera import (
    PrecioCarreraCreate,
    PrecioCarreraEstadoUpdate,
    PrecioCarreraResponse,
    TipoPrecio,
)
from app.services.precio_carrera_service import (
    PrecioCarreraService,
)


router = APIRouter(
    prefix="/precios",
    tags=["Precios"],
)


@router.post(
    "",
    response_model=PrecioCarreraResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_precio(
    data: PrecioCarreraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PRECIOS_GESTIONAR
        )
    ),
):
    return PrecioCarreraService.crear(
        db,
        data,
    )


@router.get(
    "",
    response_model=list[PrecioCarreraResponse],
)
def listar_precios(
    id_carrera_ciclo: int | None = Query(
        default=None
    ),
    id_grado: int | None = Query(
        default=None
    ),
    tipo: TipoPrecio | None = Query(
        default=None
    ),
    activo: bool | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return PrecioCarreraService.listar(
        db=db,
        id_carrera_ciclo=id_carrera_ciclo,
        id_grado=id_grado,
        tipo=tipo,
        activo=activo,
    )


@router.get(
    "/{id_precio}",
    response_model=PrecioCarreraResponse,
)
def obtener_precio(
    id_precio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return PrecioCarreraService.obtener(
        db,
        id_precio,
    )


@router.patch(
    "/{id_precio}/estado",
    response_model=PrecioCarreraResponse,
)
def cambiar_estado_precio(
    id_precio: int,
    data: PrecioCarreraEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PRECIOS_GESTIONAR
        )
    ),
):
    return PrecioCarreraService.cambiar_estado(
        db,
        id_precio,
        data,
    )
    