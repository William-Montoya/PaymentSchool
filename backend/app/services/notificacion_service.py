from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.repositories.contacto_repository import (
    ContactoRepository,
)
from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.repositories.notificacion_repository import (
    NotificacionRepository,
)
from app.schemas.notificacion import (
    NotificacionCreate,
    NotificacionDeudaCreate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class NotificacionService:

    @staticmethod
    def obtener(
        db: Session,
        id_notificacion: int,
    ) -> dict:

        notificacion = (
            NotificacionRepository
            .get_by_id(
                db,
                id_notificacion,
            )
        )

        if notificacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada",
            )

        return notificacion

    @staticmethod
    def buscar_contactos(
        db: Session,
        buscar: str | None,
        limit: int,
    ) -> list[dict]:

        return (
            NotificacionRepository
            .buscar_contactos(
                db=db,
                buscar=buscar,
                limit=limit,
            )
        )

    @staticmethod
    def crear(
        db: Session,
        data: NotificacionCreate,
        id_usuario: int,
    ) -> dict:

        # Eliminar ids repetidos conservando orden.
        ids_contacto = list(
            dict.fromkeys(
                data.ids_contacto
            )
        )

        contactos = []

        for id_contacto in ids_contacto:

            contacto = (
                ContactoRepository
                .get_by_id(
                    db,
                    id_contacto,
                )
            )

            if contacto is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Contacto {id_contacto} "
                        "no encontrado"
                    ),
                )

            if not contacto.activo:
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"El contacto {id_contacto} "
                        "está inactivo"
                    ),
                )

            contactos.append(contacto)

        try:
            id_notificacion = (
                NotificacionRepository
                .crear(
                    db=db,
                    titulo=data.titulo.strip(),
                    mensaje=data.mensaje.strip(),
                    id_usuario=id_usuario,
                )
            )

            for contacto in contactos:
                (
                    NotificacionRepository
                    .agregar_destinatario(
                        db=db,
                        id_notificacion=
                            id_notificacion,
                        id_contacto=
                            contacto.id_contacto,
                    )
                )

            notificacion = (
                NotificacionService
                .obtener(
                    db,
                    id_notificacion,
                )
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="NOTIFICACIONES",
                accion="CREAR_NOTIFICACION",
                tabla_afectada="notificacion",
                id_registro=id_notificacion,
                descripcion=(
                    "Creación de notificación"
                ),
                datos_nuevos=notificacion,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible registrar "
                        "la notificación"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return notificacion

    @staticmethod
    def generar_aviso_deuda(
        db: Session,
        id_estudiante: int,
        data: NotificacionDeudaCreate,
        id_usuario: int,
    ) -> dict:

        estudiante = (
            EstudianteRepository
            .get_by_id(
                db,
                id_estudiante,
            )
        )

        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        deuda = (
            NotificacionRepository
            .obtener_deuda_estudiante(
                db,
                id_estudiante,
            )
        )

        if deuda is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El estudiante no presenta "
                    "saldo pendiente"
                ),
            )

        deuda_total = Decimal(
            deuda["deuda_total"]
        )

        if deuda_total <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El estudiante no presenta "
                    "saldo pendiente"
                ),
            )

        if data.id_contacto is not None:

            contacto = (
                ContactoRepository
                .get_by_id(
                    db,
                    data.id_contacto,
                )
            )

            if contacto is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail="Contacto no encontrado",
                )

            if (
                contacto.id_estudiante
                != id_estudiante
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "El contacto no pertenece "
                        "al estudiante"
                    ),
                )

            if not contacto.activo:
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail="El contacto está inactivo",
                )

            id_contacto = (
                contacto.id_contacto
            )

            nombre_contacto = (
                contacto.nombre
            )

        else:

            contacto = (
                NotificacionRepository
                .get_contacto_preferido(
                    db,
                    id_estudiante,
                )
            )

            if contacto is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "El estudiante no posee "
                        "un contacto activo"
                    ),
                )

            id_contacto = (
                contacto["id_contacto"]
            )

            nombre_contacto = (
                contacto["nombre"]
            )

        titulo = (
            "Aviso de saldo pendiente"
        )

        mensaje = (
            f"Estimado/a {nombre_contacto}, "
            f"se informa que el estudiante "
            f"{deuda['estudiante']} "
            f"({deuda['codigo_estudiante']}) "
            f"presenta un saldo pendiente de "
            f"Q{deuda_total:.2f}. "
            f"Por favor, comuníquese con "
            f"administración para revisar "
            f"su estado de cuenta."
        )

        try:
            id_notificacion = (
                NotificacionRepository
                .crear(
                    db=db,
                    titulo=titulo,
                    mensaje=mensaje,
                    id_usuario=id_usuario,
                )
            )

            (
                NotificacionRepository
                .agregar_destinatario(
                    db=db,
                    id_notificacion=
                        id_notificacion,
                    id_contacto=
                        id_contacto,
                )
            )

            resultado = (
                NotificacionService
                .obtener(
                    db,
                    id_notificacion,
                )
            )

            resultado["deuda_total"] = (
                deuda_total
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="NOTIFICACIONES",
                accion="AVISO_DEUDA",
                tabla_afectada="notificacion",
                id_registro=id_notificacion,
                descripcion=(
                    "Generación de aviso de deuda "
                    f"para estudiante {id_estudiante}"
                ),
                datos_nuevos=resultado,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible generar "
                        "el aviso de deuda"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado

    @staticmethod
    def marcar_abierto(
        db: Session,
        id_destinatario: int,
        id_usuario: int,
    ) -> dict:

        destinatario = (
            NotificacionRepository
            .get_destinatario(
                db,
                id_destinatario,
            )
        )

        if destinatario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destinatario no encontrado",
            )

        # Operación idempotente.
        if destinatario["estado"] == "ABIERTO":
            return destinatario

        try:
            (
                NotificacionRepository
                .marcar_abierto(
                    db,
                    id_destinatario,
                )
            )

            resultado = (
                NotificacionRepository
                .get_destinatario(
                    db,
                    id_destinatario,
                )
            )

            if resultado is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "El destinatario fue actualizado, "
                        "pero no pudo recuperarse"
                    ),
                )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="NOTIFICACIONES",
                accion="ABRIR_NOTIFICACION",
                tabla_afectada=
                    "notificacion_destinatario",
                id_registro=id_destinatario,
                descripcion=(
                    "Notificación marcada como abierta"
                ),
                datos_anteriores=destinatario,
                datos_nuevos=resultado,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible marcar "
                        "la notificación como abierta"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return resultado