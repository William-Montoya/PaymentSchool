from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.models.inscripcion import Inscripcion
from app.models.obligacion import Obligacion
from app.repositories.catalogo_academico_repository import (
    CatalogoAcademicoRepository,
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
from app.repositories.precio_carrera_repository import (
    PrecioCarreraRepository,
)
from app.schemas.inscripcion import (
    InscripcionCreate,
    InscripcionEstadoUpdate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class InscripcionService:

    @staticmethod
    def _cantidad_meses(
        fecha_inicio: date,
        fecha_fin: date,
    ) -> int:
        return (
            (
                fecha_fin.year
                - fecha_inicio.year
            )
            * 12
            + (
                fecha_fin.month
                - fecha_inicio.month
            )
            + 1
        )

    @staticmethod
    def _periodos_mensuales(
        fecha_inicio: date,
        cantidad_meses: int,
    ) -> set[str]:
        periodos: set[str] = set()

        year = fecha_inicio.year
        month = fecha_inicio.month

        for desplazamiento in range(
            cantidad_meses
        ):
            total_meses = (
                year * 12
                + (month - 1)
                + desplazamiento
            )

            periodo_year = (
                total_meses // 12
            )

            periodo_month = (
                total_meses % 12
                + 1
            )

            periodos.add(
                (
                    f"{periodo_year:04d}-"
                    f"{periodo_month:02d}"
                )
            )

        return periodos

    @staticmethod
    def _generar_obligacion_unica(
        db: Session,
        inscripcion: Inscripcion,
        precio,
        tipo_obligacion: str,
        fecha_vencimiento: date,
    ) -> Obligacion:

        obligacion = Obligacion(
            id_inscripcion=(
                inscripcion.id_inscripcion
            ),
            id_precio=precio.id_precio,
            concepto=precio.concepto,
            periodo=None,
            fecha_vencimiento=(
                fecha_vencimiento
            ),
            monto_bruto=precio.monto,
            monto_neto=precio.monto,
            tipo_obligacion=(
                tipo_obligacion
            ),
        )

        return ObligacionRepository.create(
            db,
            obligacion,
        )

    @staticmethod
    def _generar_obligaciones_automaticas(
        db: Session,
        inscripcion: Inscripcion,
        ciclo,
    ) -> dict:

        precios = PrecioCarreraRepository.list(
            db=db,
            id_carrera_ciclo=(
                inscripcion.id_carrera_ciclo
            ),
            id_grado=inscripcion.id_grado,
            activo=True,
        )

        if not precios:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No existen tarifas activas "
                    "configuradas para la carrera "
                    "y grado seleccionados"
                ),
            )

        precios_inscripcion = [
            precio
            for precio in precios
            if precio.tipo == "INSCRIPCION"
        ]

        precios_mensualidad = [
            precio
            for precio in precios
            if precio.tipo == "MENSUALIDAD"
        ]

        precios_otros = [
            precio
            for precio in precios
            if precio.tipo == "OTRO"
        ]

        if not precios_inscripcion:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No existe una tarifa activa "
                    "de inscripción para la "
                    "carrera y grado seleccionados"
                ),
            )

        if not precios_mensualidad:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No existe una tarifa activa "
                    "de mensualidad para la "
                    "carrera y grado seleccionados"
                ),
            )

        tarifas_inscripcion_aplicables = [
            precio
            for precio in precios_inscripcion
            if (
                precio.fecha_inicio
                <= ciclo.fecha_fin
                and (
                    precio.fecha_fin is None
                    or precio.fecha_fin
                    >= ciclo.fecha_inicio
                )
            )
        ]

        if not tarifas_inscripcion_aplicables:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No existe una tarifa de "
                    "inscripción aplicable al "
                    "ciclo escolar seleccionado"
                ),
            )

        if (
            len(
                tarifas_inscripcion_aplicables
            )
            > 1
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Existe más de una tarifa de "
                    "inscripción aplicable al "
                    "mismo ciclo, carrera y grado"
                ),
            )

        tarifa_inscripcion = (
            tarifas_inscripcion_aplicables[0]
        )

        fecha_vencimiento_inscripcion = max(
            tarifa_inscripcion.fecha_inicio,
            ciclo.fecha_inicio,
        )

        InscripcionService._generar_obligacion_unica(
            db=db,
            inscripcion=inscripcion,
            precio=tarifa_inscripcion,
            tipo_obligacion="INSCRIPCION",
            fecha_vencimiento=(
                fecha_vencimiento_inscripcion
            ),
        )

        cantidad_inscripcion = 1

        periodos_generados: set[str] = set()

        cantidad_mensualidades = 0

        monto_mensualidades = Decimal(
            "0.00"
        )

        for precio in precios_mensualidad:

            fecha_inicio = max(
                precio.fecha_inicio,
                ciclo.fecha_inicio,
            )

            fecha_fin = min(
                (
                    precio.fecha_fin
                    if precio.fecha_fin
                    is not None
                    else ciclo.fecha_fin
                ),
                ciclo.fecha_fin,
            )

            if fecha_fin < fecha_inicio:
                continue

            cantidad_meses = (
                InscripcionService
                ._cantidad_meses(
                    fecha_inicio,
                    fecha_fin,
                )
            )

            periodos = (
                InscripcionService
                ._periodos_mensuales(
                    fecha_inicio,
                    cantidad_meses,
                )
            )

            repetidos = (
                periodos_generados
                .intersection(
                    periodos
                )
            )

            if repetidos:
                periodos_texto = ", ".join(
                    sorted(repetidos)
                )

                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "Existen tarifas de "
                        "mensualidad que se "
                        "superponen en los períodos: "
                        f"{periodos_texto}"
                    ),
                )

            ObligacionRepository.generar_mensualidades(
                db=db,
                id_inscripcion=(
                    inscripcion.id_inscripcion
                ),
                id_precio=precio.id_precio,
                fecha_inicio=fecha_inicio,
                cantidad_meses=cantidad_meses,
            )

            periodos_generados.update(
                periodos
            )

            cantidad_mensualidades += (
                cantidad_meses
            )

            monto_mensualidades += (
                precio.monto
                * cantidad_meses
            )

        if cantidad_mensualidades == 0:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Las tarifas de mensualidad "
                    "configuradas no generan ningún "
                    "período dentro del ciclo escolar"
                ),
            )

        cantidad_otros = 0

        monto_otros = Decimal(
            "0.00"
        )

        for precio in precios_otros:

            InscripcionService._generar_obligacion_unica(
                db=db,
                inscripcion=inscripcion,
                precio=precio,
                tipo_obligacion="OTRO",
                fecha_vencimiento=(
                    precio.fecha_inicio
                ),
            )

            cantidad_otros += 1

            monto_otros += precio.monto

        monto_inscripcion = (
            tarifa_inscripcion.monto
        )

        total_programado = (
            monto_inscripcion
            + monto_mensualidades
            + monto_otros
        )

        return {
            "id_inscripcion": (
                inscripcion.id_inscripcion
            ),
            "id_carrera_ciclo": (
                inscripcion.id_carrera_ciclo
            ),
            "id_grado": (
                inscripcion.id_grado
            ),
            "tarifa_inscripcion": {
                "id_precio": (
                    tarifa_inscripcion
                    .id_precio
                ),
                "concepto": (
                    tarifa_inscripcion
                    .concepto
                ),
                "monto": str(
                    monto_inscripcion
                ),
            },
            "cantidad_inscripcion": (
                cantidad_inscripcion
            ),
            "cantidad_mensualidades": (
                cantidad_mensualidades
            ),
            "cantidad_otros": (
                cantidad_otros
            ),
            "total_obligaciones": (
                cantidad_inscripcion
                + cantidad_mensualidades
                + cantidad_otros
            ),
            "monto_mensualidades": str(
                monto_mensualidades
            ),
            "monto_otros": str(
                monto_otros
            ),
            "total_programado": str(
                total_programado
            ),
        }

    @staticmethod
    def crear(
        db: Session,
        data: InscripcionCreate,
        id_usuario: int,
    ) -> dict:

        estudiante = (
            EstudianteRepository
            .get_by_id(
                db,
                data.id_estudiante,
            )
        )

        if estudiante is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Estudiante no encontrado"
                ),
            )

        carrera_ciclo = (
            CatalogoAcademicoRepository
            .get_carrera_ciclo(
                db,
                data.id_carrera_ciclo,
            )
        )

        if carrera_ciclo is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Carrera/ciclo no encontrada"
                ),
            )

        if not carrera_ciclo.estado:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La carrera no está activa "
                    "en este ciclo"
                ),
            )

        ciclo = (
            CatalogoAcademicoRepository
            .get_ciclo(
                db,
                carrera_ciclo.id_ciclo,
            )
        )

        if ciclo is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Ciclo escolar no encontrado"
                ),
            )

        if ciclo.estado == "CERRADO":
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No pueden registrarse "
                    "inscripciones en un "
                    "ciclo cerrado"
                ),
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
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Grado no encontrado"
                ),
            )

        if not grado.activo:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El grado está inactivo"
                ),
            )

        if (
            grado.id_carrera_ciclo
            != data.id_carrera_ciclo
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El grado no pertenece a "
                    "la carrera/ciclo "
                    "seleccionada"
                ),
            )

        activa = (
            InscripcionRepository
            .get_activa_en_ciclo(
                db,
                data.id_estudiante,
                carrera_ciclo.id_ciclo,
            )
        )

        if activa:
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "El estudiante ya tiene "
                    "una inscripción activa en "
                    "este ciclo escolar"
                ),
            )

        inscripcion = Inscripcion(
            **data.model_dump()
        )

        try:
            db.add(inscripcion)
            db.flush()
            db.refresh(inscripcion)

            resumen_financiero = (
                InscripcionService
                ._generar_obligaciones_automaticas(
                    db=db,
                    inscripcion=inscripcion,
                    ciclo=ciclo,
                )
            )

            resultado = (
                InscripcionRepository
                .get_detalle(
                    db,
                    inscripcion.id_inscripcion,
                )
            )

            if resultado is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "La inscripción fue "
                        "registrada, pero no "
                        "pudo recuperarse"
                    ),
                )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="ACADEMICO",
                accion="CREAR_INSCRIPCION",
                tabla_afectada=(
                    "inscripcion"
                ),
                id_registro=(
                    inscripcion
                    .id_inscripcion
                ),
                descripcion=(
                    "Creación de inscripción "
                    "para estudiante "
                    f"{data.id_estudiante}"
                ),
                datos_nuevos=resultado,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion=(
                    "GENERAR_OBLIGACIONES_"
                    "AUTOMATICAS"
                ),
                tabla_afectada=(
                    "obligacion"
                ),
                id_registro=None,
                descripcion=(
                    "Generación automática "
                    "de obligaciones para "
                    "inscripción "
                    f"{inscripcion.id_inscripcion}"
                ),
                datos_nuevos=(
                    resumen_financiero
                ),
            )

            db.commit()

        except HTTPException:
            db.rollback()
            raise

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "No fue posible registrar "
                    "la inscripción y sus "
                    "obligaciones"
                ),
            )

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    get_postgres_error_message(
                        exc,
                        (
                            "No fue posible "
                            "registrar la "
                            "inscripción y sus "
                            "obligaciones"
                        ),
                    )
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def obtener(
        db: Session,
        id_inscripcion: int,
    ) -> dict:

        inscripcion = (
            InscripcionRepository
            .get_detalle(
                db,
                id_inscripcion,
            )
        )

        if inscripcion is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Inscripción no encontrada"
                ),
            )

        return inscripcion

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_inscripcion: int,
        data: InscripcionEstadoUpdate,
        id_usuario: int,
    ) -> dict:

        inscripcion = (
            InscripcionRepository
            .get_by_id(
                db,
                id_inscripcion,
            )
        )

        if inscripcion is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Inscripción no encontrada"
                ),
            )

        if (
            inscripcion.estado
            == data.estado
        ):
            return (
                InscripcionRepository
                .get_detalle(
                    db,
                    id_inscripcion,
                )
            )

        if (
            inscripcion.estado
            != "ACTIVA"
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Una inscripción cerrada "
                    "no puede cambiar "
                    "nuevamente de estado"
                ),
            )

        if data.estado == "ACTIVA":
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La inscripción ya está "
                    "activa"
                ),
            )

        datos_anteriores = (
            InscripcionRepository
            .get_detalle(
                db,
                id_inscripcion,
            )
        )

        try:
            inscripcion.estado = (
                data.estado
            )

            db.flush()
            db.refresh(inscripcion)

            resultado = (
                InscripcionRepository
                .get_detalle(
                    db,
                    id_inscripcion,
                )
            )

            if resultado is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "La inscripción fue "
                        "modificada, pero no "
                        "pudo recuperarse"
                    ),
                )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="ACADEMICO",
                accion=(
                    "CAMBIAR_ESTADO_"
                    "INSCRIPCION"
                ),
                tabla_afectada=(
                    "inscripcion"
                ),
                id_registro=(
                    id_inscripcion
                ),
                descripcion=(
                    "Cambio de estado de "
                    "inscripción "
                    f"{id_inscripcion}: "
                    f"{datos_anteriores['estado']} "
                    f"→ {resultado['estado']}"
                ),
                datos_anteriores=(
                    datos_anteriores
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except DBAPIError:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No fue posible cambiar "
                    "el estado de la "
                    "inscripción"
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado