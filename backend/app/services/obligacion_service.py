from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.models.obligacion import Obligacion
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.repositories.obligacion_repository import (
    ObligacionRepository,
)
from app.repositories.precio_carrera_repository import (
    PrecioCarreraRepository,
)
from app.schemas.obligacion import (
    GenerarMensualidadesCreate,
    ObligacionDesdePrecioCreate,
    ObligacionManualCreate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class ObligacionService:

    @staticmethod
    def _obtener_inscripcion_activa(
        db: Session,
        id_inscripcion: int,
    ):
        inscripcion = InscripcionRepository.get_by_id(
            db,
            id_inscripcion,
        )

        if inscripcion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inscripción no encontrada",
            )

        if inscripcion.estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Solo pueden generarse obligaciones "
                    "para inscripciones activas"
                ),
            )

        return inscripcion

    @staticmethod
    def obtener(
        db: Session,
        id_obligacion: int,
    ) -> dict:

        obligacion = ObligacionRepository.get_con_saldo(
            db,
            id_obligacion,
        )

        if obligacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obligación no encontrada",
            )

        return obligacion

    @staticmethod
    def listar(
        db: Session,
        id_inscripcion: int | None = None,
        estado: str | None = None,
        tipo_obligacion: str | None = None,
    ):
        return ObligacionRepository.list_con_saldo(
            db=db,
            id_inscripcion=id_inscripcion,
            estado=estado,
            tipo_obligacion=tipo_obligacion,
        )

    @staticmethod
    def crear_desde_precio(
        db: Session,
        data: ObligacionDesdePrecioCreate,
        id_usuario: int,
    ) -> dict:

        inscripcion = (
            ObligacionService
            ._obtener_inscripcion_activa(
                db,
                data.id_inscripcion,
            )
        )

        precio = PrecioCarreraRepository.get_by_id(
            db,
            data.id_precio,
        )

        if precio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Precio no encontrado",
            )

        if not precio.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio está inactivo",
            )

        if (
            precio.id_carrera_ciclo
            != inscripcion.id_carrera_ciclo
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El precio no pertenece a la "
                    "carrera/ciclo de la inscripción"
                ),
            )

        if (
            precio.id_grado
            != inscripcion.id_grado
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El precio no pertenece al "
                    "grado de la inscripción"
                ),
            )

        if precio.tipo == "MENSUALIDAD":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Las mensualidades deben generarse "
                    "con el proceso de mensualidades"
                ),
            )

        if (
            data.fecha_vencimiento
            < precio.fecha_inicio
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La obligación está fuera "
                    "de la vigencia del precio"
                ),
            )

        if (
            precio.fecha_fin is not None
            and data.fecha_vencimiento
            > precio.fecha_fin
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La obligación está fuera "
                    "de la vigencia del precio"
                ),
            )

        if ObligacionRepository.existe_desde_precio(
            db,
            data.id_inscripcion,
            data.id_precio,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Ya existe una obligación activa "
                    "generada desde este precio"
                ),
            )

        tipo_obligacion = (
            "INSCRIPCION"
            if precio.tipo == "INSCRIPCION"
            else "OTRO"
        )

        obligacion = Obligacion(
            id_inscripcion=data.id_inscripcion,
            id_precio=data.id_precio,
            concepto=precio.concepto,
            periodo=None,
            fecha_vencimiento=data.fecha_vencimiento,
            monto_bruto=precio.monto,
            monto_neto=precio.monto,
            tipo_obligacion=tipo_obligacion,
        )

        try:
            ObligacionRepository.create(
                db,
                obligacion,
            )

            resultado = ObligacionService.obtener(
                db,
                obligacion.id_obligacion,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="CREAR_OBLIGACION_DESDE_PRECIO",
                tabla_afectada="obligacion",
                id_registro=obligacion.id_obligacion,
                descripcion=(
                    "Creación de obligación desde precio "
                    f"{data.id_precio}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible crear "
                    "la obligación"
                ),
            )

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible crear "
                        "la obligación"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def crear_manual(
        db: Session,
        data: ObligacionManualCreate,
        id_usuario: int,
    ) -> dict:

        ObligacionService._obtener_inscripcion_activa(
            db,
            data.id_inscripcion,
        )

        obligacion = Obligacion(
            id_inscripcion=data.id_inscripcion,
            id_precio=None,
            concepto=data.concepto,
            periodo=data.periodo,
            fecha_vencimiento=data.fecha_vencimiento,
            monto_bruto=data.monto_bruto,
            monto_neto=data.monto_bruto,
            tipo_obligacion=data.tipo_obligacion,
        )

        try:
            ObligacionRepository.create(
                db,
                obligacion,
            )

            resultado = ObligacionService.obtener(
                db,
                obligacion.id_obligacion,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="CREAR_OBLIGACION_MANUAL",
                tabla_afectada="obligacion",
                id_registro=obligacion.id_obligacion,
                descripcion=(
                    "Creación manual de obligación "
                    f"para inscripción "
                    f"{data.id_inscripcion}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible crear "
                    "la obligación"
                ),
            )

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible crear "
                        "la obligación"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def generar_mensualidades(
        db: Session,
        data: GenerarMensualidadesCreate,
        id_usuario: int,
    ) -> dict:

        inscripcion = (
            ObligacionService
            ._obtener_inscripcion_activa(
                db,
                data.id_inscripcion,
            )
        )

        precio = PrecioCarreraRepository.get_by_id(
            db,
            data.id_precio,
        )

        if precio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Precio no encontrado",
            )

        if not precio.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio está inactivo",
            )

        if precio.tipo != "MENSUALIDAD":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El precio seleccionado "
                    "no es de mensualidad"
                ),
            )

        if (
            precio.id_carrera_ciclo
            != inscripcion.id_carrera_ciclo
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El precio no pertenece a "
                    "la carrera/ciclo de la inscripción"
                ),
            )

        if (
            precio.id_grado
            != inscripcion.id_grado
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El precio no pertenece al "
                    "grado de la inscripción"
                ),
            )

        if data.fecha_inicio < precio.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La fecha inicial está fuera "
                    "de la vigencia del precio"
                ),
            )

        if (
            precio.fecha_fin is not None
            and data.fecha_inicio > precio.fecha_fin
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La fecha inicial está fuera "
                    "de la vigencia del precio"
                ),
            )

        try:
            ObligacionRepository.generar_mensualidades(
                db=db,
                id_inscripcion=data.id_inscripcion,
                id_precio=data.id_precio,
                fecha_inicio=data.fecha_inicio,
                cantidad_meses=data.cantidad_meses,
            )

            resultado = {
                "mensaje": (
                    "Mensualidades generadas correctamente"
                ),
                "id_inscripcion": data.id_inscripcion,
                "id_precio": data.id_precio,
                "fecha_inicio": data.fecha_inicio,
                "cantidad_meses": data.cantidad_meses,
            }

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="GENERAR_MENSUALIDADES",
                tabla_afectada="obligacion",
                id_registro=None,
                descripcion=(
                    "Generación de mensualidades "
                    f"para inscripción "
                    f"{data.id_inscripcion}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            mensaje = get_postgres_error_message(
                exc,
                (
                    "No fue posible generar "
                    "las mensualidades"
                ),
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=mensaje,
            )

        except Exception:
            db.rollback()
            raise

        return resultado