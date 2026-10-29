from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    FINANZAS_VER,
    PAGOS_REGISTRAR,
)
from app.models.usuario import Usuario
from app.schemas.pago import (
    AplicarSaldoFavorCreate,
    AplicarSaldoFavorResponse,
    EstadoSaldoFavor,
    SaldoFavorResponse,
)
from app.services.saldo_favor_service import (
    SaldoFavorService,
)


router = APIRouter(
    prefix="/saldos-favor",
    tags=["Saldos a favor"],
)


@router.get(
    "",
    response_model=list[SaldoFavorResponse],
)
def listar_saldos(
    id_estudiante: int | None = Query(default=None),
    estado: EstadoSaldoFavor | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return SaldoFavorService.listar(
        db=db,
        id_estudiante=id_estudiante,
        estado=estado,
    )


@router.get(
    "/{id_saldo_favor}",
    response_model=SaldoFavorResponse,
)
def obtener_saldo(
    id_saldo_favor: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return SaldoFavorService.obtener(
        db,
        id_saldo_favor,
    )


@router.post(
    "/{id_saldo_favor}/aplicar",
    response_model=AplicarSaldoFavorResponse,
)
def aplicar_saldo(
    id_saldo_favor: int,
    data: AplicarSaldoFavorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            PAGOS_REGISTRAR
        )
    ),
):
    return SaldoFavorService.aplicar(
        db,
        id_saldo_favor,
        data,
        current_user.id_usuario,
    )