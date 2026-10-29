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
    FINANZAS_VER,
    PAGOS_ANULAR,
    PAGOS_REGISTRAR,
)
from app.models.usuario import Usuario
from app.repositories.pago_repository import (
    PagoRepository,
)
from app.schemas.pago import (
    AplicacionPagoCreate,
    AplicacionPagoResponse,
    CobroCreate,
    CobroResponse,
    ComprobantePagoResponse,
    EstadoPago,
    PagoAnular,
    PagoAutomaticoCreate,
    PagoAutomaticoResponse,
    PagoCreate,
    PagoResponse,
    ReciboResponse,
)
from app.services.pago_service import (
    PagoService,
)


router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
)


@router.post(
    "",
    response_model=PagoResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def registrar_pago(
    data: PagoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PAGOS_REGISTRAR
        )
    ),
):
    return PagoService.registrar(
        db,
        data,
        current_user.id_usuario,
    )


@router.post(
    "/automatico",
    response_model=
        PagoAutomaticoResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def registrar_pago_automatico(
    data: PagoAutomaticoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PAGOS_REGISTRAR
        )
    ),
):
    return (
        PagoService
        .registrar_automatico(
            db,
            data,
            current_user
                .id_usuario,
        )
    )


@router.post(
    "/cobro",
    response_model=CobroResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def registrar_cobro(
    data: CobroCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PAGOS_REGISTRAR
        )
    ),
):
    return (
        PagoService
        .registrar_cobro(
            db,
            data,
            current_user
                .id_usuario,
        )
    )


@router.get(
    "",
    response_model=
        list[PagoResponse],
)
def listar_pagos(
    id_estudiante: int | None = (
        Query(default=None)
    ),
    estado: EstadoPago | None = (
        Query(default=None)
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return PagoService.listar(
        db=db,
        id_estudiante=
            id_estudiante,
        estado=estado,
    )


@router.get(
    "/{id_pago}",
    response_model=PagoResponse,
)
def obtener_pago(
    id_pago: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return PagoService.obtener(
        db,
        id_pago,
    )


@router.get(
    "/{id_pago}/comprobante",
    response_model=
        ComprobantePagoResponse,
)
def obtener_comprobante(
    id_pago: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return (
        PagoService
        .obtener_comprobante(
            db,
            id_pago,
        )
    )


@router.post(
    "/{id_pago}/aplicaciones",
    response_model=
        AplicacionPagoResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def aplicar_pago(
    id_pago: int,
    data: AplicacionPagoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PAGOS_REGISTRAR
        )
    ),
):
    return PagoService.aplicar(
        db,
        id_pago,
        data,
        current_user.id_usuario,
    )


@router.get(
    "/{id_pago}/aplicaciones",
    response_model=
        list[
            AplicacionPagoResponse
        ],
)
def listar_aplicaciones(
    id_pago: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    PagoService.obtener(
        db,
        id_pago,
    )

    return (
        PagoRepository
        .list_aplicaciones(
            db,
            id_pago,
        )
    )


@router.post(
    "/{id_pago}/recibo",
    response_model=
        ReciboResponse,
)
def generar_recibo(
    id_pago: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PAGOS_REGISTRAR
        )
    ),
):
    return (
        PagoService
        .generar_recibo(
            db,
            id_pago,
            current_user
                .id_usuario,
        )
    )


@router.post(
    "/{id_pago}/anular",
    response_model=PagoResponse,
)
def anular_pago(
    id_pago: int,
    data: PagoAnular,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PAGOS_ANULAR
        )
    ),
):
    return PagoService.anular(
        db,
        id_pago,
        data,
        current_user.id_usuario,
    )