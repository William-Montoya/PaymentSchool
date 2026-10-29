from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.precio_carrera import PrecioCarrera
from app.repositories.catalogo_academico_repository import (
    CatalogoAcademicoRepository,
)
from app.repositories.precio_carrera_repository import (
    PrecioCarreraRepository,
)
from app.schemas.precio_carrera import (
    PrecioCarreraCreate,
    PrecioCarreraEstadoUpdate,
)


class PrecioCarreraService:

    @staticmethod
    def obtener(
        db: Session,
        id_precio: int,
    ) -> PrecioCarrera:

        precio = PrecioCarreraRepository.get_by_id(
            db,
            id_precio,
        )

        if precio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Precio no encontrado",
            )

        return precio

    @staticmethod
    def listar(
        db: Session,
        id_carrera_ciclo: int | None = None,
        id_grado: int | None = None,
        tipo: str | None = None,
        activo: bool | None = None,
    ):
        return PrecioCarreraRepository.list(
            db=db,
            id_carrera_ciclo=id_carrera_ciclo,
            id_grado=id_grado,
            tipo=tipo,
            activo=activo,
        )

    @staticmethod
    def crear(
        db: Session,
        data: PrecioCarreraCreate,
    ) -> PrecioCarrera:

        carrera_ciclo = (
            CatalogoAcademicoRepository
            .get_carrera_ciclo(
                db,
                data.id_carrera_ciclo,
            )
        )

        if carrera_ciclo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrera/ciclo no encontrada",
            )

        if not carrera_ciclo.estado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La carrera/ciclo está inactiva",
            )

        grado = (
            CatalogoAcademicoRepository
            .get_grado(
                db,
                data.id_grado,
            )
        )

        if grado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grado no encontrado",
            )

        if not grado.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El grado está inactivo",
            )

        if (
            grado.id_carrera_ciclo
            != data.id_carrera_ciclo
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El grado no pertenece a "
                    "la carrera/ciclo seleccionada"
                ),
            )

        if (
            data.fecha_fin is not None
            and data.fecha_fin < data.fecha_inicio
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La fecha final no puede ser "
                    "anterior a la fecha inicial"
                ),
            )

        solapado = (
            PrecioCarreraRepository
            .buscar_solapado(
                db=db,
                id_carrera_ciclo=data.id_carrera_ciclo,
                id_grado=data.id_grado,
                tipo=data.tipo,
                concepto=data.concepto,
                fecha_inicio=data.fecha_inicio,
                fecha_fin=data.fecha_fin,
            )
        )

        if solapado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Ya existe un precio activo para "
                    "ese grado y concepto en el "
                    "período indicado"
                ),
            )

        precio = PrecioCarrera(
            **data.model_dump()
        )

        try:
            db.add(precio)
            db.commit()
            db.refresh(precio)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible registrar el precio",
            )

        return precio

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_precio: int,
        data: PrecioCarreraEstadoUpdate,
    ) -> PrecioCarrera:

        precio = PrecioCarreraService.obtener(
            db,
            id_precio,
        )

        if precio.activo == data.activo:
            return precio

        if data.activo:
            if precio.id_grado is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "No puede activarse un precio "
                        "sin grado asignado"
                    ),
                )

            grado = (
                CatalogoAcademicoRepository
                .get_grado(
                    db,
                    precio.id_grado,
                )
            )

            if grado is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Grado no encontrado",
                )

            if not grado.activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El grado está inactivo",
                )

            if (
                grado.id_carrera_ciclo
                != precio.id_carrera_ciclo
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "El grado no pertenece a "
                        "la carrera/ciclo del precio"
                    ),
                )

            conflicto = (
                PrecioCarreraRepository
                .buscar_solapado(
                    db=db,
                    id_carrera_ciclo=(
                        precio.id_carrera_ciclo
                    ),
                    id_grado=precio.id_grado,
                    tipo=precio.tipo,
                    concepto=precio.concepto,
                    fecha_inicio=precio.fecha_inicio,
                    fecha_fin=precio.fecha_fin,
                    excluir_id=precio.id_precio,
                )
            )

            if conflicto:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "No puede activarse porque existe "
                        "otro precio vigente para el "
                        "mismo grado"
                    ),
                )

        precio.activo = data.activo

        db.commit()
        db.refresh(precio)

        return precio