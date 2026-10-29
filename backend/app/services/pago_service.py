from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.core.db_errors import get_postgres_error_message
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.recibo_repository import ReciboRepository
from app.repositories.saldo_favor_repository import SaldoFavorRepository
from app.schemas.pago import (
    AplicacionPagoCreate,
    CobroCreate,
    PagoAnular,
    PagoAutomaticoCreate,
    PagoCreate,
)
from app.services.auditoria_service import AuditoriaService


class PagoService:

    @staticmethod
    def obtener(
        db: Session,
        id_pago: int,
    ) -> dict:
        pago = PagoRepository.get_by_id(
            db,
            id_pago,
        )

        if pago is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado",
            )

        return pago

    @staticmethod
    def listar(
        db: Session,
        id_estudiante: int | None = None,
        estado: str | None = None,
    ):
        return PagoRepository.list(
            db=db,
            id_estudiante=id_estudiante,
            estado=estado,
        )

    @staticmethod
    def _validar_obligaciones_cobro(
        id_estudiante: int,
        ids_obligaciones: list[int],
        obligaciones: list[dict],
    ) -> None:
        if not ids_obligaciones:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe seleccionar al menos una obligación",
            )

        if any(
            id_obligacion <= 0
            for id_obligacion in ids_obligaciones
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las obligaciones seleccionadas no son válidas",
            )

        if len(set(ids_obligaciones)) != len(ids_obligaciones):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No puede seleccionar la misma obligación "
                    "más de una vez"
                ),
            )

        if len(obligaciones) != len(ids_obligaciones):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Una o más obligaciones seleccionadas no existen"
                ),
            )

        for obligacion in obligaciones:
            if obligacion["id_estudiante"] != id_estudiante:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Todas las obligaciones seleccionadas deben "
                        "pertenecer al mismo estudiante"
                    ),
                )

            if obligacion["estado"] not in {"PENDIENTE", "PARCIAL"}:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"La obligación {obligacion['concepto']} "
                        "ya no está pendiente de pago"
                    ),
                )

            if Decimal(obligacion["saldo"]) <= Decimal("0"):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"La obligación {obligacion['concepto']} "
                        "no tiene saldo pendiente"
                    ),
                )

    @staticmethod
    def _validar_secuencia_mensualidades(
        db: Session,
        obligaciones: list[dict],
    ) -> None:
        seleccionadas_por_inscripcion: dict[int, set[int]] = {}

        for obligacion in obligaciones:
            if obligacion["tipo_obligacion"] != "MENSUALIDAD":
                continue

            id_inscripcion = obligacion["id_inscripcion"]

            if id_inscripcion not in seleccionadas_por_inscripcion:
                seleccionadas_por_inscripcion[id_inscripcion] = set()

            seleccionadas_por_inscripcion[id_inscripcion].add(
                obligacion["id_obligacion"]
            )

        for id_inscripcion, ids_seleccionados in (
            seleccionadas_por_inscripcion.items()
        ):
            abiertas = PagoRepository.list_mensualidades_abiertas(
                db,
                id_inscripcion,
            )

            cantidad_seleccionada = len(ids_seleccionados)

            primeras_permitidas = {
                obligacion["id_obligacion"]
                for obligacion in abiertas[:cantidad_seleccionada]
            }

            if primeras_permitidas == ids_seleccionados:
                continue

            faltante = None

            for mensualidad in abiertas:
                if mensualidad["id_obligacion"] not in ids_seleccionados:
                    faltante = mensualidad
                    break

            if faltante is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "La selección de mensualidades no respeta "
                        "el orden cronológico"
                    ),
                )

            periodo = faltante["periodo"] or faltante["concepto"]

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No puede pagar una mensualidad posterior mientras "
                    "exista una mensualidad anterior pendiente. "
                    f"Primero debe pagar {periodo}."
                ),
            )

    @staticmethod
    def registrar_cobro(
        db: Session,
        data: CobroCreate,
        id_usuario: int,
    ) -> dict:
        estudiante = EstudianteRepository.get_by_id(
            db,
            data.id_estudiante,
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        if len(data.id_obligaciones) != len(set(data.id_obligaciones)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No puede seleccionar la misma obligación "
                    "más de una vez"
                ),
            )

        try:
            ids_bloqueados = PagoRepository.bloquear_obligaciones(
                db,
                data.id_obligaciones,
            )

            if len(ids_bloqueados) != len(data.id_obligaciones):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        "Una o más obligaciones seleccionadas no existen"
                    ),
                )

            obligaciones = PagoRepository.get_obligaciones_cobro(
                db,
                data.id_obligaciones,
            )

            PagoService._validar_obligaciones_cobro(
                id_estudiante=data.id_estudiante,
                ids_obligaciones=data.id_obligaciones,
                obligaciones=obligaciones,
            )

            PagoService._validar_secuencia_mensualidades(
                db,
                obligaciones,
            )

            total_seleccionado = sum(
                (
                    Decimal(obligacion["saldo"])
                    for obligacion in obligaciones
                ),
                Decimal("0.00"),
            )

            if data.monto > total_seleccionado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "El monto recibido supera el saldo total de las "
                        "obligaciones seleccionadas"
                    ),
                )

            id_pago = PagoRepository.registrar(
                db=db,
                id_estudiante=data.id_estudiante,
                monto=data.monto,
                metodo=data.metodo,
                referencia=data.referencia,
                observaciones=data.observaciones,
                id_usuario=id_usuario,
            )

            saldo_pago = Decimal(data.monto)

            for obligacion in obligaciones:
                if saldo_pago <= Decimal("0"):
                    break

                saldo_obligacion = Decimal(obligacion["saldo"])
                monto_aplicar = min(
                    saldo_pago,
                    saldo_obligacion,
                )

                PagoRepository.aplicar(
                    db=db,
                    id_pago=id_pago,
                    id_obligacion=obligacion["id_obligacion"],
                    monto=monto_aplicar,
                )

                saldo_pago -= monto_aplicar

            if saldo_pago != Decimal("0"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "No fue posible aplicar completamente el monto "
                        "del pago"
                    ),
                )

            id_recibo = ReciboRepository.generar(
                db,
                id_pago,
            )

            recibo = ReciboRepository.get_by_id(
                db,
                id_recibo,
            )

            if recibo is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "El recibo fue generado, pero no pudo recuperarse"
                    ),
                )

            pago = PagoService.obtener(
                db,
                id_pago,
            )

            aplicaciones = PagoRepository.list_aplicaciones_detalle(
                db,
                id_pago,
            )

            total_aplicado = sum(
                (
                    Decimal(aplicacion["monto_aplicado"])
                    for aplicacion in aplicaciones
                ),
                Decimal("0.00"),
            )

            resultado = {
                "pago": pago,
                "recibo": recibo,
                "aplicaciones": aplicaciones,
                "total_seleccionado": total_seleccionado,
                "total_aplicado": total_aplicado,
                "saldo_seleccionado_restante": (
                    total_seleccionado - total_aplicado
                ),
            }

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="REGISTRAR_COBRO",
                tabla_afectada="pago",
                id_registro=id_pago,
                descripcion=(
                    "Registro de cobro con aplicación seleccionada "
                    f"para estudiante {data.id_estudiante}"
                ),
                datos_nuevos={
                    "pago": pago,
                    "recibo": recibo,
                    "id_obligaciones": data.id_obligaciones,
                    "total_seleccionado": str(total_seleccionado),
                    "total_aplicado": str(total_aplicado),
                },
            )

            db.commit()

        except HTTPException:
            db.rollback()
            raise

        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible registrar el cobro",
                ),
            )

        except DBAPIError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible registrar el cobro",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def obtener_comprobante(
        db: Session,
        id_pago: int,
    ) -> dict:
        pago = PagoService.obtener(
            db,
            id_pago,
        )

        recibo = ReciboRepository.get_by_pago(
            db,
            id_pago,
        )

        aplicaciones = PagoRepository.list_aplicaciones_detalle(
            db,
            id_pago,
        )

        return {
            "pago": pago,
            "recibo": recibo,
            "aplicaciones": aplicaciones,
        }

    @staticmethod
    def registrar(
        db: Session,
        data: PagoCreate,
        id_usuario: int,
    ) -> dict:
        estudiante = EstudianteRepository.get_by_id(
            db,
            data.id_estudiante,
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        try:
            id_pago = PagoRepository.registrar(
                db=db,
                id_estudiante=data.id_estudiante,
                monto=data.monto,
                metodo=data.metodo,
                referencia=data.referencia,
                observaciones=data.observaciones,
                id_usuario=id_usuario,
            )

            pago = PagoService.obtener(
                db,
                id_pago,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="REGISTRAR_PAGO",
                tabla_afectada="pago",
                id_registro=id_pago,
                descripcion="Registro de pago",
                datos_nuevos=pago,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible registrar el pago",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return pago

    @staticmethod
    def registrar_automatico(
        db: Session,
        data: PagoAutomaticoCreate,
        id_usuario: int,
    ) -> dict:
        estudiante = EstudianteRepository.get_by_id(
            db,
            data.id_estudiante,
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        try:
            id_pago = PagoRepository.registrar_automatico(
                db=db,
                id_estudiante=data.id_estudiante,
                monto=data.monto,
                metodo=data.metodo,
                referencia=data.referencia,
                observaciones=data.observaciones,
                id_usuario=id_usuario,
            )

            pago = PagoService.obtener(
                db,
                id_pago,
            )

            saldo = SaldoFavorRepository.get_activo_by_pago(
                db,
                id_pago,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="REGISTRAR_PAGO_AUTOMATICO",
                tabla_afectada="pago",
                id_registro=id_pago,
                descripcion="Registro de pago automático",
                datos_nuevos={
                    "pago": pago,
                    "saldo_favor": saldo,
                },
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible registrar el pago automático",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return {
            "pago": pago,
            "saldo_favor": saldo,
        }

    @staticmethod
    def aplicar(
        db: Session,
        id_pago: int,
        data: AplicacionPagoCreate,
        id_usuario: int,
    ) -> dict:
        pago_anterior = PagoService.obtener(
            db,
            id_pago,
        )

        if pago_anterior["estado"] != "CONFIRMADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo pueden aplicarse pagos confirmados",
            )

        saldo_favor = SaldoFavorRepository.get_activo_by_pago(
            db,
            id_pago,
        )

        if saldo_favor is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Este pago tiene saldo a favor activo. "
                    "El excedente debe aplicarse desde el módulo "
                    "de saldo a favor."
                ),
            )

        try:
            id_aplicacion = PagoRepository.aplicar(
                db=db,
                id_pago=id_pago,
                id_obligacion=data.id_obligacion,
                monto=data.monto,
            )

            aplicacion = PagoRepository.get_aplicacion(
                db,
                id_aplicacion,
            )

            if aplicacion is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "La aplicación fue registrada, pero no pudo "
                        "recuperarse"
                    ),
                )

            pago_actualizado = PagoService.obtener(
                db,
                id_pago,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="APLICAR_PAGO",
                tabla_afectada="aplicacion_pago",
                id_registro=id_aplicacion,
                descripcion=(
                    f"Aplicación del pago {id_pago} a la obligación "
                    f"{data.id_obligacion}"
                ),
                datos_anteriores={
                    "pago": pago_anterior,
                },
                datos_nuevos={
                    "aplicacion": aplicacion,
                    "pago": pago_actualizado,
                },
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible aplicar el pago",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return aplicacion

    @staticmethod
    def anular(
        db: Session,
        id_pago: int,
        data: PagoAnular,
        id_usuario: int,
    ) -> dict:
        pago_anterior = PagoService.obtener(
            db,
            id_pago,
        )

        if pago_anterior["estado"] == "ANULADO":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pago ya está anulado",
            )

        try:
            PagoRepository.anular(
                db=db,
                id_pago=id_pago,
                motivo=data.motivo,
                id_usuario=id_usuario,
            )

            pago_anulado = PagoService.obtener(
                db,
                id_pago,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="ANULAR_PAGO",
                tabla_afectada="pago",
                id_registro=id_pago,
                descripcion=(
                    f"Anulación de pago. Motivo: {data.motivo}"
                ),
                datos_anteriores=pago_anterior,
                datos_nuevos={
                    "pago": pago_anulado,
                    "motivo_anulacion": data.motivo,
                },
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible anular el pago",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return pago_anulado

    @staticmethod
    def generar_recibo(
        db: Session,
        id_pago: int,
        id_usuario: int,
    ) -> dict:
        pago = PagoService.obtener(
            db,
            id_pago,
        )

        existente = ReciboRepository.get_by_pago(
            db,
            id_pago,
        )

        if existente is not None:
            return existente

        if pago["estado"] != "CONFIRMADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Solo puede generarse recibo para un pago confirmado"
                ),
            )

        try:
            id_recibo = ReciboRepository.generar(
                db,
                id_pago,
            )

            recibo = ReciboRepository.get_by_id(
                db,
                id_recibo,
            )

            if recibo is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "El recibo fue generado, pero no pudo recuperarse"
                    ),
                )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="GENERAR_RECIBO",
                tabla_afectada="recibo",
                id_registro=id_recibo,
                descripcion=f"Generación de recibo para el pago {id_pago}",
                datos_nuevos={
                    "recibo": recibo,
                    "pago": pago,
                },
            )

            db.commit()

        except IntegrityError:
            db.rollback()

            existente = ReciboRepository.get_by_pago(
                db,
                id_pago,
            )

            if existente is not None:
                return existente

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible generar el recibo",
            )

        except DBAPIError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible generar el recibo",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return recibo
