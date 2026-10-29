from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.repositories.cambio_carrera_repository import (
    CambioCarreraRepository,
)
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.repositories.movimiento_saldo_repository import (
    MovimientoSaldoRepository,
)
from app.schemas.movimiento_saldo import (
    TrasladoSaldoCreate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class MovimientoSaldoService:

    @staticmethod
    def obtener(
        db: Session,
        id_movimiento: int,
    ) -> dict:

        movimiento = (
            MovimientoSaldoRepository
            .get_by_id(
                db,
                id_movimiento,
            )
        )

        if movimiento is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Movimiento de saldo no encontrado"
                ),
            )

        return movimiento

    @staticmethod
    def trasladar(
        db: Session,
        data: TrasladoSaldoCreate,
        id_usuario: int,
    ) -> dict:

        if (
            data.id_inscripcion_origen
            == data.id_inscripcion_destino
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La inscripción origen y destino "
                    "no pueden ser la misma"
                ),
            )

        origen = (
            InscripcionRepository
            .get_by_id(
                db,
                data.id_inscripcion_origen,
            )
        )

        if origen is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Inscripción origen no encontrada"
                ),
            )

        destino = (
            InscripcionRepository
            .get_by_id(
                db,
                data.id_inscripcion_destino,
            )
        )

        if destino is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Inscripción destino no encontrada"
                ),
            )

        if (
            origen.id_estudiante
            != data.id_estudiante
            or destino.id_estudiante
            != data.id_estudiante
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Las inscripciones deben pertenecer "
                    "al estudiante indicado"
                ),
            )

        # Para TRASLADO_SALDO exigimos que exista
        # un cambio de carrera aprobado entre las
        # dos inscripciones.
        existe_cambio = (
            CambioCarreraRepository
            .existe_cambio_aprobado(
                db=db,
                id_estudiante=data.id_estudiante,
                id_inscripcion_origen=
                    data.id_inscripcion_origen,
                id_inscripcion_destino=
                    data.id_inscripcion_destino,
            )
        )

        if not existe_cambio:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No existe un cambio de carrera "
                    "aprobado entre las inscripciones "
                    "indicadas"
                ),
            )

        if origen.estado != "FINALIZADA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La inscripción origen debe estar "
                    "finalizada"
                ),
            )

        if destino.estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La inscripción destino debe "
                    "estar activa"
                ),
            )

        datos_anteriores = {
            "id_estudiante":
                data.id_estudiante,
            "id_inscripcion_origen":
                data.id_inscripcion_origen,
            "estado_inscripcion_origen":
                origen.estado,
            "id_inscripcion_destino":
                data.id_inscripcion_destino,
            "estado_inscripcion_destino":
                destino.estado,
        }

        try:
            id_movimiento = (
                MovimientoSaldoRepository
                .trasladar(
                    db=db,
                    id_estudiante=
                        data.id_estudiante,
                    id_inscripcion_origen=
                        data.id_inscripcion_origen,
                    id_inscripcion_destino=
                        data.id_inscripcion_destino,
                    monto=data.monto,
                    motivo=data.motivo,
                    id_usuario=id_usuario,
                )
            )

            if data.referencia is not None:
                (
                    MovimientoSaldoRepository
                    .actualizar_referencia(
                        db,
                        id_movimiento,
                        data.referencia,
                    )
                )

            movimiento = (
                MovimientoSaldoService
                .obtener(
                    db,
                    id_movimiento,
                )
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="TRASLADO_SALDO",
                tabla_afectada="movimiento_saldo",
                id_registro=id_movimiento,
                descripcion=(
                    "Traslado de saldo del estudiante "
                    f"{data.id_estudiante}"
                ),
                datos_anteriores=
                    datos_anteriores,
                datos_nuevos=movimiento,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible registrar "
                        "el traslado de saldo"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return movimiento