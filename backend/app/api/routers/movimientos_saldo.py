from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    FINANZAS_VER,
    SALDOS_GESTIONAR,
)
from app.models.usuario import Usuario
from app.repositories.movimiento_saldo_repository import (
    MovimientoSaldoRepository,
)
from app.schemas.movimiento_saldo import (
    EstadoMovimientoSaldo,
    MovimientoSaldoResponse,
    TipoMovimientoSaldo,
    TrasladoSaldoCreate,
)
from app.services.movimiento_saldo_service import (
    MovimientoSaldoService,
)


router = APIRouter(
    prefix="/movimientos-saldo",
    tags=["Movimientos de saldo"],
)


@router.post(
    "/trasladar",
    response_model=MovimientoSaldoResponse,
    status_code=status.HTTP_201_CREATED,
)
def trasladar_saldo(
    data: TrasladoSaldoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            SALDOS_GESTIONAR
        )
    ),
):
    return MovimientoSaldoService.trasladar(
        db,
        data,
        current_user.id_usuario,
    )


@router.get(
    "",
    response_model=list[
        MovimientoSaldoResponse
    ],
)
def listar_movimientos(
    id_estudiante: int | None = Query(
        default=None
    ),
    tipo: TipoMovimientoSaldo | None = Query(
        default=None
    ),
    estado: EstadoMovimientoSaldo | None = Query(
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
        MovimientoSaldoRepository
        .list(
            db=db,
            id_estudiante=id_estudiante,
            tipo=tipo,
            estado=estado,
        )
    )


@router.get(
    "/{id_movimiento}",
    response_model=MovimientoSaldoResponse,
)
def obtener_movimiento(
    id_movimiento: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return MovimientoSaldoService.obtener(
        db,
        id_movimiento,
    )