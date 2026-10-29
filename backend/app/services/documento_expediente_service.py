from datetime import date
from pathlib import Path

from fastapi import (
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.storage import (
    eliminar_archivo,
    guardar_archivo_expediente,
    obtener_media_type,
    resolver_ruta_archivo,
)
from app.models.documento_expediente import (
    DocumentoExpediente,
)
from app.repositories.documento_expediente_repository import (
    DocumentoExpedienteRepository,
)
from app.repositories.expediente_repository import (
    ExpedienteRepository,
)
from app.repositories.tipo_documento_repository import (
    TipoDocumentoRepository,
)
from app.schemas.documento_expediente import (
    DocumentoEntregaUpdate,
)


class DocumentoExpedienteService:

    @staticmethod
    def obtener(
        db: Session,
        id_expediente: int,
        id_documento: int,
    ) -> DocumentoExpediente:

        documento = (
            DocumentoExpedienteRepository
            .get_by_id(
                db,
                id_documento,
            )
        )

        if documento is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado",
            )

        if (
            documento.id_expediente
            != id_expediente
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "El documento no pertenece "
                    "al expediente indicado"
                ),
            )

        return documento

    @staticmethod
    def cambiar_entrega(
        db: Session,
        id_expediente: int,
        id_tipo_documento: int,
        data: DocumentoEntregaUpdate,
    ) -> DocumentoExpediente:

        expediente = (
            ExpedienteRepository
            .get_by_id(
                db,
                id_expediente,
            )
        )

        if expediente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expediente no encontrado",
            )

        tipo = (
            TipoDocumentoRepository
            .get_by_id(
                db,
                id_tipo_documento,
            )
        )

        if tipo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Tipo de documento no encontrado"
                ),
            )

        if not tipo.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El tipo de documento está inactivo"
                ),
            )

        documento = (
            DocumentoExpedienteRepository
            .get_by_expediente_tipo(
                db=db,
                id_expediente=id_expediente,
                id_tipo_documento=id_tipo_documento,
            )
        )

        if documento is None:
            documento = DocumentoExpediente(
                id_expediente=id_expediente,
                id_tipo_documento=id_tipo_documento,
                nombre_archivo=None,
                ruta_archivo=None,
                entregado=data.entregado,
                fecha_entrega=(
                    date.today()
                    if data.entregado
                    else None
                ),
            )

            try:
                (
                    DocumentoExpedienteRepository
                    .crear(
                        db,
                        documento,
                    )
                )

                db.commit()
                db.refresh(documento)

            except IntegrityError:
                db.rollback()

                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "No fue posible registrar "
                        "el estado del documento"
                    ),
                )

            return documento

        documento.entregado = (
            data.entregado
        )

        documento.fecha_entrega = (
            date.today()
            if data.entregado
            else None
        )

        try:
            db.commit()
            db.refresh(documento)

        except Exception:
            db.rollback()
            raise

        return documento

    @staticmethod
    def subir(
        db: Session,
        id_expediente: int,
        id_tipo_documento: int,
        archivo: UploadFile,
    ) -> DocumentoExpediente:

        expediente = (
            ExpedienteRepository
            .get_by_id(
                db,
                id_expediente,
            )
        )

        if expediente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expediente no encontrado",
            )

        tipo = (
            TipoDocumentoRepository
            .get_by_id(
                db,
                id_tipo_documento,
            )
        )

        if tipo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Tipo de documento no encontrado"
                ),
            )

        if not tipo.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El tipo de documento está inactivo"
                ),
            )

        existente = (
            DocumentoExpedienteRepository
            .get_by_expediente_tipo(
                db=db,
                id_expediente=id_expediente,
                id_tipo_documento=id_tipo_documento,
            )
        )

        if (
            existente is not None
            and existente.ruta_archivo
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Este tipo de documento ya tiene "
                    "un archivo registrado. "
                    "Utilice reemplazar archivo."
                ),
            )

        try:
            stored = (
                guardar_archivo_expediente(
                    archivo,
                    id_expediente,
                )
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        if existente is None:
            documento = DocumentoExpediente(
                id_expediente=id_expediente,
                id_tipo_documento=id_tipo_documento,
                nombre_archivo=stored.original_name,
                ruta_archivo=stored.relative_path,
                entregado=False,
                fecha_entrega=None,
            )

            try:
                (
                    DocumentoExpedienteRepository
                    .crear(
                        db,
                        documento,
                    )
                )

                db.commit()
                db.refresh(documento)

            except IntegrityError:
                db.rollback()

                eliminar_archivo(
                    stored.relative_path
                )

                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "No fue posible registrar "
                        "el documento"
                    ),
                )

            except Exception:
                db.rollback()

                eliminar_archivo(
                    stored.relative_path
                )

                raise

            return documento

        existente.nombre_archivo = (
            stored.original_name
        )

        existente.ruta_archivo = (
            stored.relative_path
        )

        try:
            db.commit()
            db.refresh(existente)

        except Exception:
            db.rollback()

            eliminar_archivo(
                stored.relative_path
            )

            raise

        return existente

    @staticmethod
    def reemplazar(
        db: Session,
        id_expediente: int,
        id_documento: int,
        archivo: UploadFile,
    ) -> DocumentoExpediente:

        documento = (
            DocumentoExpedienteService
            .obtener(
                db,
                id_expediente,
                id_documento,
            )
        )

        ruta_anterior = (
            documento.ruta_archivo
        )

        try:
            nuevo = (
                guardar_archivo_expediente(
                    archivo,
                    id_expediente,
                )
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        documento.nombre_archivo = (
            nuevo.original_name
        )

        documento.ruta_archivo = (
            nuevo.relative_path
        )

        try:
            db.commit()
            db.refresh(documento)

        except Exception:
            db.rollback()

            eliminar_archivo(
                nuevo.relative_path
            )

            raise

        eliminar_archivo(
            ruta_anterior
        )

        return documento

    @staticmethod
    def preparar_descarga(
        db: Session,
        id_expediente: int,
        id_documento: int,
    ) -> tuple[
        DocumentoExpediente,
        Path,
        str,
    ]:

        documento = (
            DocumentoExpedienteService
            .obtener(
                db,
                id_expediente,
                id_documento,
            )
        )

        if not documento.ruta_archivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "El documento no tiene "
                    "un archivo disponible"
                ),
            )

        try:
            path = resolver_ruta_archivo(
                documento.ruta_archivo
            )

        except ValueError:
            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "La ruta almacenada "
                    "del documento es inválida"
                ),
            )

        if not path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "El registro existe, pero el archivo "
                    "físico no está disponible"
                ),
            )

        nombre = (
            documento.nombre_archivo
            or path.name
        )

        media_type = obtener_media_type(
            nombre
        )

        return (
            documento,
            path,
            media_type,
        )