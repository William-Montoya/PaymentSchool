from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.repositories.auditoria_repository import (
    AuditoriaRepository,
)


class AuditoriaService:

    @staticmethod
    def registrar(
        db: Session,
        id_usuario: int | None,
        modulo: str,
        accion: str,
        tabla_afectada: str | None,
        id_registro: int | None,
        descripcion: str | None,
        datos_anteriores: Any | None = None,
        datos_nuevos: Any | None = None,
    ) -> None:

        anteriores = (
            jsonable_encoder(
                datos_anteriores
            )
            if datos_anteriores is not None
            else None
        )

        nuevos = (
            jsonable_encoder(
                datos_nuevos
            )
            if datos_nuevos is not None
            else None
        )

        AuditoriaRepository.registrar(
            db=db,
            id_usuario=id_usuario,
            modulo=modulo.strip().upper(),
            accion=accion.strip().upper(),
            tabla_afectada=(
                tabla_afectada.strip().lower()
                if tabla_afectada
                else None
            ),
            id_registro=id_registro,
            descripcion=(
                descripcion.strip()
                if descripcion
                else None
            ),
            datos_anteriores=anteriores,
            datos_nuevos=nuevos,
        )

    @staticmethod
    def obtener(
        db: Session,
        id_auditoria: int,
    ) -> dict:

        auditoria = (
            AuditoriaRepository
            .get_by_id(
                db,
                id_auditoria,
            )
        )

        if auditoria is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Registro de auditoria "
                    "no encontrado"
                ),
            )

        return auditoria

    @staticmethod
    def listar(
        db: Session,
        id_usuario: int | None = None,
        modulo: str | None = None,
        accion: str | None = None,
        tabla_afectada: str | None = None,
        id_registro: int | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:

        return AuditoriaRepository.list(
            db=db,
            id_usuario=id_usuario,
            modulo=modulo,
            accion=accion,
            tabla_afectada=tabla_afectada,
            id_registro=id_registro,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            offset=offset,
            limit=limit,
        )

    @staticmethod
    def catalogos(
        db: Session,
    ) -> dict:

        return AuditoriaRepository.catalogos(
            db
        )
