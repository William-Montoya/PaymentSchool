from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.api.dependencies.auth import (
    require_permission,
)
from app.core.database import get_db
from app.core.permissions import (
    EXPEDIENTES_GESTIONAR,
    EXPEDIENTES_VER,
)
from app.models.usuario import Usuario
from app.schemas.documento_expediente import (
    DocumentoEntregaUpdate,
    DocumentoExpedienteResponse,
)
from app.services.documento_expediente_service import (
    DocumentoExpedienteService,
)


router = APIRouter(
    prefix="/expedientes",
    tags=["Documentos de expediente"],
)


# ============================================================
# SUBIR ARCHIVO
# ============================================================

@router.post(
    "/{id_expediente}/documentos/"
    "{id_tipo_documento}",
    response_model=DocumentoExpedienteResponse,
    status_code=status.HTTP_201_CREATED,
)
def subir_documento(
    id_expediente: int,
    id_tipo_documento: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return DocumentoExpedienteService.subir(
        db=db,
        id_expediente=id_expediente,
        id_tipo_documento=id_tipo_documento,
        archivo=archivo,
    )


# ============================================================
# OBTENER METADATOS
# ============================================================

@router.get(
    "/{id_expediente}/documentos/"
    "{id_documento}",
    response_model=DocumentoExpedienteResponse,
)
def obtener_documento(
    id_expediente: int,
    id_documento: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_VER
        )
    ),
):
    return DocumentoExpedienteService.obtener(
        db,
        id_expediente,
        id_documento,
    )


# ============================================================
# MARCAR ENTREGADO / PENDIENTE
# ============================================================

@router.patch(
    "/{id_expediente}/documentos/"
    "{id_tipo_documento}/entrega",
    response_model=DocumentoExpedienteResponse,
)
def cambiar_entrega(
    id_expediente: int,
    id_tipo_documento: int,
    data: DocumentoEntregaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return (
        DocumentoExpedienteService
        .cambiar_entrega(
            db=db,
            id_expediente=id_expediente,
            id_tipo_documento=id_tipo_documento,
            data=data,
        )
    )


# ============================================================
# REEMPLAZAR ARCHIVO
# ============================================================

@router.put(
    "/{id_expediente}/documentos/"
    "{id_documento}/archivo",
    response_model=DocumentoExpedienteResponse,
)
def reemplazar_archivo(
    id_expediente: int,
    id_documento: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_GESTIONAR
        )
    ),
):
    return (
        DocumentoExpedienteService
        .reemplazar(
            db=db,
            id_expediente=id_expediente,
            id_documento=id_documento,
            archivo=archivo,
        )
    )


# ============================================================
# DESCARGAR / VISTA PREVIA
# ============================================================

@router.get(
    "/{id_expediente}/documentos/"
    "{id_documento}/descargar",
)
def descargar_documento(
    id_expediente: int,
    id_documento: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permission(
            EXPEDIENTES_VER
        )
    ),
):
    (
        documento,
        path,
        media_type,
    ) = (
        DocumentoExpedienteService
        .preparar_descarga(
            db=db,
            id_expediente=id_expediente,
            id_documento=id_documento,
        )
    )

    return FileResponse(
        path=str(path),
        filename=(
            documento.nombre_archivo
            or path.name
        ),
        media_type=media_type,
    )