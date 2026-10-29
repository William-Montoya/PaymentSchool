from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.models.descuento import Descuento
from app.repositories.descuento_repository import (
    DescuentoRepository,
)
from app.repositories.obligacion_repository import (
    ObligacionRepository,
)
from app.schemas.descuento import (
    DescuentoCreate,
    DescuentoEstadoUpdate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class DescuentoService:

    @staticmethod
    def crear(
        db: Session,
        data: DescuentoCreate,
        id_usuario: int,
    ) -> Descuento:

        existente = (
            DescuentoRepository
            .get_by_nombre(
                db,
                data.nombre,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Ya existe un descuento "
                    "con ese nombre"
                ),
            )

        descuento = Descuento(
            **data.model_dump()
        )

        try:
            db.add(descuento)
            db.flush()
            db.refresh(descuento)

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="CREAR_DESCUENTO",
                tabla_afectada="descuento",
                id_registro=descuento.id_descuento,
                descripcion=(
                    f"Creación de descuento "
                    f"{descuento.nombre}"
                ),
                datos_nuevos=descuento,
            )

            db.commit()
            db.refresh(descuento)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible registrar "
                    "el descuento"
                ),
            )

        except Exception:
            db.rollback()
            raise

        return descuento

    @staticmethod
    def listar(
        db: Session,
        activo: bool | None = None,
    ):
        return DescuentoRepository.list(
            db,
            activo,
        )

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_descuento: int,
        data: DescuentoEstadoUpdate,
        id_usuario: int,
    ) -> Descuento:

        descuento = (
            DescuentoRepository
            .get_by_id(
                db,
                id_descuento,
            )
        )

        if descuento is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Descuento no encontrado",
            )

        datos_anteriores = {
            "id_descuento":
                descuento.id_descuento,
            "activo":
                descuento.activo,
        }

        try:
            descuento.activo = data.activo

            db.flush()
            db.refresh(descuento)

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="CAMBIAR_ESTADO_DESCUENTO",
                tabla_afectada="descuento",
                id_registro=id_descuento,
                descripcion=(
                    "Cambio de estado del descuento "
                    f"{id_descuento}"
                ),
                datos_anteriores=
                    datos_anteriores,
                datos_nuevos=descuento,
            )

            db.commit()
            db.refresh(descuento)

        except Exception:
            db.rollback()
            raise

        return descuento

    @staticmethod
    def aplicar(
        db: Session,
        id_descuento: int,
        id_obligacion: int,
        id_usuario: int,
    ) -> dict:

        descuento = (
            DescuentoRepository
            .get_by_id(
                db,
                id_descuento,
            )
        )

        if descuento is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Descuento no encontrado",
            )

        if not descuento.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El descuento está inactivo",
            )

        obligacion = (
            ObligacionRepository
            .get_con_saldo(
                db,
                id_obligacion,
            )
        )

        if obligacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obligación no encontrada",
            )

        if obligacion["estado"] != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El descuento solo puede aplicarse "
                    "a una obligación pendiente"
                ),
            )

        if Decimal(
            obligacion["total_pagado"]
        ) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No puede modificarse una obligación "
                    "que ya recibió pagos"
                ),
            )

        existente = (
            DescuentoRepository
            .get_aplicacion_existente(
                db,
                id_descuento,
                id_obligacion,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Este descuento ya fue aplicado "
                    "a la obligación"
                ),
            )

        obligacion_anterior = obligacion

        try:
            DescuentoRepository.aplicar(
                db=db,
                id_descuento=id_descuento,
                id_obligacion=id_obligacion,
            )

            aplicaciones = (
                DescuentoRepository
                .list_aplicaciones(
                    db,
                    id_obligacion=id_obligacion,
                    id_descuento=id_descuento,
                )
            )

            if not aplicaciones:
                raise HTTPException(
                    status_code=
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "El descuento fue aplicado, "
                        "pero no pudo recuperarse"
                    ),
                )

            aplicacion = aplicaciones[0]

            obligacion_actualizada = (
                ObligacionRepository
                .get_con_saldo(
                    db,
                    id_obligacion,
                )
            )

            if obligacion_actualizada is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "La obligación fue modificada, "
                        "pero no pudo recuperarse"
                    ),
                )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="APLICAR_DESCUENTO",
                tabla_afectada=
                    "descuento_obligacion",
                id_registro=(
                    aplicacion[
                        "id_descuento_obligacion"
                    ]
                ),
                descripcion=(
                    f"Aplicación de descuento "
                    f"{id_descuento} a la obligación "
                    f"{id_obligacion}"
                ),
                datos_anteriores={
                    "obligacion":
                        obligacion_anterior,
                },
                datos_nuevos={
                    "aplicacion":
                        aplicacion,
                    "obligacion":
                        obligacion_actualizada,
                },
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible aplicar el descuento",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return aplicacion