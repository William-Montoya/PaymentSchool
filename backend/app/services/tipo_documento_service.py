from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tipo_documento import TipoDocumento
from app.repositories.tipo_documento_repository import (
    TipoDocumentoRepository,
)
from app.schemas.tipo_documento import (
    TipoDocumentoCreate,
    TipoDocumentoEstadoUpdate,
    TipoDocumentoUpdate,
)


class TipoDocumentoService:

    @staticmethod
    def obtener(
        db: Session,
        id_tipo_documento: int,
    ) -> TipoDocumento:

        tipo = TipoDocumentoRepository.get_by_id(
            db,
            id_tipo_documento,
        )

        if tipo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado",
            )

        return tipo

    @staticmethod
    def crear(
        db: Session,
        data: TipoDocumentoCreate,
    ) -> TipoDocumento:

        existente = (
            TipoDocumentoRepository
            .get_by_nombre(
                db,
                data.nombre,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Ya existe un tipo de documento "
                    "con ese nombre"
                ),
            )

        tipo = TipoDocumento(
            **data.model_dump()
        )

        try:
            db.add(tipo)
            db.commit()
            db.refresh(tipo)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible registrar "
                    "el tipo de documento"
                ),
            )

        return tipo

    @staticmethod
    def actualizar(
        db: Session,
        id_tipo_documento: int,
        data: TipoDocumentoUpdate,
    ) -> TipoDocumento:

        tipo = TipoDocumentoService.obtener(
            db,
            id_tipo_documento,
        )

        cambios = data.model_dump(
            exclude_unset=True
        )

        if "nombre" in cambios:
            existente = (
                TipoDocumentoRepository
                .get_by_nombre(
                    db,
                    cambios["nombre"],
                )
            )

            if (
                existente
                and existente.id_tipo_documento
                != id_tipo_documento
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Ya existe un tipo de documento "
                        "con ese nombre"
                    ),
                )

        for campo, valor in cambios.items():
            setattr(
                tipo,
                campo,
                valor,
            )

        db.commit()
        db.refresh(tipo)

        return tipo

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_tipo_documento: int,
        data: TipoDocumentoEstadoUpdate,
    ) -> TipoDocumento:

        tipo = TipoDocumentoService.obtener(
            db,
            id_tipo_documento,
        )

        tipo.activo = data.activo

        db.commit()
        db.refresh(tipo)

        return tipo