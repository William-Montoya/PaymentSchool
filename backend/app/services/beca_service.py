from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.models.beca import Beca
from app.models.beca_estudiante import (
    BecaEstudiante,
)
from app.repositories.beca_repository import (
    BecaRepository,
)
from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.repositories.obligacion_repository import (
    ObligacionRepository,
)
from app.schemas.beca import (
    BecaCreate,
    BecaEstadoUpdate,
    BecaEstudianteCreate,
    BecaEstudianteFinalizar,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class BecaService:

    @staticmethod
    def crear(
        db: Session,
        data: BecaCreate,
        id_usuario: int,
    ) -> Beca:

        if (
            data.fecha_inicio is not None
            and data.fecha_fin is not None
            and data.fecha_fin < data.fecha_inicio
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La fecha final no puede ser "
                    "anterior a la fecha inicial"
                ),
            )

        existente = BecaRepository.get_by_nombre(
            db,
            data.nombre,
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una beca con ese nombre",
            )

        beca = Beca(
            **data.model_dump()
        )

        try:
            db.add(beca)
            db.flush()
            db.refresh(beca)

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="CREAR_BECA",
                tabla_afectada="beca",
                id_registro=beca.id_beca,
                descripcion=(
                    f"Creación de beca {beca.nombre}"
                ),
                datos_nuevos=beca,
            )

            db.commit()
            db.refresh(beca)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible registrar la beca",
            )

        except Exception:
            db.rollback()
            raise

        return beca

    @staticmethod
    def listar(
        db: Session,
        estado: str | None = None,
    ):
        return BecaRepository.list(
            db,
            estado,
        )

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_beca: int,
        data: BecaEstadoUpdate,
        id_usuario: int,
    ) -> Beca:

        beca = BecaRepository.get_by_id(
            db,
            id_beca,
        )

        if beca is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beca no encontrada",
            )

        datos_anteriores = {
            "id_beca": beca.id_beca,
            "estado": beca.estado,
        }

        try:
            beca.estado = data.estado

            db.flush()
            db.refresh(beca)

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="CAMBIAR_ESTADO_BECA",
                tabla_afectada="beca",
                id_registro=id_beca,
                descripcion=(
                    f"Cambio de estado de beca "
                    f"{id_beca}"
                ),
                datos_anteriores=datos_anteriores,
                datos_nuevos=beca,
            )

            db.commit()
            db.refresh(beca)

        except Exception:
            db.rollback()
            raise

        return beca

    @staticmethod
    def asignar(
        db: Session,
        data: BecaEstudianteCreate,
        id_usuario: int,
    ) -> dict:

        beca = BecaRepository.get_by_id(
            db,
            data.id_beca,
        )

        if beca is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beca no encontrada",
            )

        if beca.estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La beca no está activa",
            )

        estudiante = (
            EstudianteRepository
            .get_by_id(
                db,
                data.id_estudiante,
            )
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
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

        if (
            beca.fecha_inicio is not None
            and data.fecha_inicio < beca.fecha_inicio
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La asignación inicia antes "
                    "de la vigencia de la beca"
                ),
            )

        if (
            beca.fecha_fin is not None
            and data.fecha_fin is not None
            and data.fecha_fin > beca.fecha_fin
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La asignación finaliza después "
                    "de la vigencia de la beca"
                ),
            )

        existente = (
            BecaRepository
            .buscar_asignacion_solapada(
                db=db,
                id_beca=data.id_beca,
                id_estudiante=data.id_estudiante,
                fecha_inicio=data.fecha_inicio,
                fecha_fin=data.fecha_fin,
            )
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El estudiante ya tiene esta beca "
                    "asignada durante ese período"
                ),
            )

        asignacion = BecaEstudiante(
            **data.model_dump()
        )

        try:
            db.add(asignacion)
            db.flush()
            db.refresh(asignacion)

            resultados = (
                BecaRepository
                .list_asignaciones(
                    db,
                    id_estudiante=data.id_estudiante,
                    id_beca=data.id_beca,
                )
            )

            resultado = next(
                item
                for item in resultados
                if item["id_beca_estudiante"]
                == asignacion.id_beca_estudiante
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="ASIGNAR_BECA",
                tabla_afectada="beca_estudiante",
                id_registro=
                    asignacion.id_beca_estudiante,
                descripcion=(
                    f"Asignación de beca "
                    f"{data.id_beca} al estudiante "
                    f"{data.id_estudiante}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def finalizar_asignacion(
        db: Session,
        id_beca_estudiante: int,
        data: BecaEstudianteFinalizar,
        id_usuario: int,
    ) -> dict:

        asignacion = (
            BecaRepository
            .get_asignacion(
                db,
                id_beca_estudiante,
            )
        )

        if asignacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignación de beca no encontrada",
            )

        if data.fecha_fin < asignacion.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La fecha final no puede ser "
                    "anterior al inicio"
                ),
            )

        datos_anteriores = {
            "id_beca_estudiante":
                asignacion.id_beca_estudiante,
            "id_beca":
                asignacion.id_beca,
            "id_estudiante":
                asignacion.id_estudiante,
            "fecha_inicio":
                asignacion.fecha_inicio,
            "fecha_fin":
                asignacion.fecha_fin,
        }

        try:
            asignacion.fecha_fin = data.fecha_fin

            db.flush()
            db.refresh(asignacion)

            resultados = (
                BecaRepository
                .list_asignaciones(
                    db,
                    id_estudiante=
                        asignacion.id_estudiante,
                    id_beca=asignacion.id_beca,
                )
            )

            resultado = next(
                item
                for item in resultados
                if item["id_beca_estudiante"]
                == id_beca_estudiante
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="FINALIZAR_BECA",
                tabla_afectada="beca_estudiante",
                id_registro=id_beca_estudiante,
                descripcion=(
                    "Finalización de asignación "
                    f"de beca {id_beca_estudiante}"
                ),
                datos_anteriores=datos_anteriores,
                datos_nuevos=resultado,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def aplicar_a_obligacion(
        db: Session,
        id_beca_estudiante: int,
        id_obligacion: int,
        id_usuario: int,
    ) -> dict:

        asignacion = (
            BecaRepository
            .get_asignacion(
                db,
                id_beca_estudiante,
            )
        )

        if asignacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignación de beca no encontrada",
            )

        beca = BecaRepository.get_by_id(
            db,
            asignacion.id_beca,
        )

        if (
            beca is None
            or beca.estado != "ACTIVA"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La beca no está activa",
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

        inscripcion = (
            InscripcionRepository
            .get_by_id(
                db,
                obligacion["id_inscripcion"],
            )
        )

        if (
            inscripcion is None
            or inscripcion.id_estudiante
            != asignacion.id_estudiante
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La obligación no pertenece "
                    "al estudiante de la beca"
                ),
            )

        if obligacion["estado"] != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La beca solo puede aplicarse "
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

        if Decimal(
            obligacion["monto_beca"]
        ) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "La obligación ya tiene "
                    "una beca aplicada"
                ),
            )

        fecha_referencia = (
            obligacion["fecha_vencimiento"]
            or date.today()
        )

        if fecha_referencia < asignacion.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La obligación es anterior "
                    "a la vigencia de la beca"
                ),
            )

        if (
            asignacion.fecha_fin is not None
            and fecha_referencia
            > asignacion.fecha_fin
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La obligación está fuera "
                    "de la vigencia de la beca"
                ),
            )

        if (
            beca.fecha_inicio is not None
            and fecha_referencia < beca.fecha_inicio
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La beca aún no estaba vigente",
            )

        if (
            beca.fecha_fin is not None
            and fecha_referencia > beca.fecha_fin
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La beca ya no estaba vigente",
            )

        obligacion_anterior = obligacion

        try:
            id_beca_obligacion = (
                BecaRepository
                .aplicar_a_obligacion(
                    db=db,
                    id_beca_estudiante=
                        id_beca_estudiante,
                    id_obligacion=
                        id_obligacion,
                )
            )

            aplicacion = (
                BecaRepository
                .get_aplicacion(
                    db,
                    id_beca_obligacion,
                )
            )

            if aplicacion is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "La beca fue aplicada, "
                        "pero no pudo recuperarse "
                        "su trazabilidad"
                    ),
                )

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
                accion="APLICAR_BECA",
                tabla_afectada="beca_obligacion",
                id_registro=id_beca_obligacion,
                descripcion=(
                    f"Aplicación de beca a la "
                    f"obligación {id_obligacion}"
                ),
                datos_anteriores={
                    "obligacion":
                        obligacion_anterior,
                },
                datos_nuevos={
                    "aplicacion": aplicacion,
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
                    "No fue posible aplicar la beca",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return aplicacion