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
    OBLIGACIONES_GESTIONAR,
)
from app.models.usuario import Usuario
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.schemas.inscripcion import (
    EstadoInscripcion,
    InscripcionDetalleResponse,
)
from app.schemas.obligacion import (
    EstadoObligacion,
    GenerarMensualidadesCreate,
    GenerarMensualidadesResponse,
    ObligacionDesdePrecioCreate,
    ObligacionManualCreate,
    ObligacionSaldoResponse,
    TipoObligacion,
)
from app.services.obligacion_service import (
    ObligacionService,
)


router = APIRouter(
    prefix="/obligaciones",
    tags=["Obligaciones"],
)


@router.post(
    "/desde-precio",
    response_model=ObligacionSaldoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_desde_precio(
    data: ObligacionDesdePrecioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            OBLIGACIONES_GESTIONAR
        )
    ),
):
    return (
        ObligacionService
        .crear_desde_precio(
            db,
            data,
            current_user.id_usuario,
        )
    )


@router.post(
    "/manual",
    response_model=ObligacionSaldoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_manual(
    data: ObligacionManualCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            OBLIGACIONES_GESTIONAR
        )
    ),
):
    return (
        ObligacionService
        .crear_manual(
            db,
            data,
            current_user.id_usuario,
        )
    )


@router.post(
    "/mensualidades",
    response_model=
        GenerarMensualidadesResponse,
)
def generar_mensualidades(
    data: GenerarMensualidadesCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            OBLIGACIONES_GESTIONAR
        )
    ),
):
    return (
        ObligacionService
        .generar_mensualidades(
            db,
            data,
            current_user.id_usuario,
        )
    )


@router.get(
    "/inscripciones",
    response_model=list[
        InscripcionDetalleResponse
    ],
)
def listar_inscripciones_finanzas(
    buscar: str | None = Query(
        default=None,
        max_length=150,
    ),
    estado: EstadoInscripcion | None = (
        Query(
            default=None
        )
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return (
        InscripcionRepository
        .list_detalle(
            db=db,
            estado=estado,
            buscar=buscar,
            limit=limit,
        )
    )


@router.get(
    "",
    response_model=list[
        ObligacionSaldoResponse
    ],
)
def listar_obligaciones(
    id_inscripcion: int | None = Query(
        default=None
    ),
    estado: EstadoObligacion | None = (
        Query(
            default=None
        )
    ),
    tipo_obligacion:
        TipoObligacion | None = Query(
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
        ObligacionService
        .listar(
            db=db,
            id_inscripcion=
                id_inscripcion,
            estado=estado,
            tipo_obligacion=
                tipo_obligacion,
        )
    )


@router.get(
    "/{id_obligacion}",
    response_model=
        ObligacionSaldoResponse,
)
def obtener_obligacion(
    id_obligacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            FINANZAS_VER
        )
    ),
):
    return (
        ObligacionService
        .obtener(
            db,
            id_obligacion,
        )
    )