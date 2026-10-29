from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.repositories.cambio_carrera_repository import (
    CambioCarreraRepository,
)
from app.repositories.catalogo_academico_repository import (
    CatalogoAcademicoRepository,
)
from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.schemas.cambio_carrera import (
    CambioCarreraCreate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class CambioCarreraService:

    @staticmethod
    def obtener(
        db: Session,
        id_cambio: int,
    ) -> dict:

        cambio = (
            CambioCarreraRepository
            .get_by_id(
                db,
                id_cambio,
            )
        )

        if cambio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Cambio de carrera no encontrado"
                ),
            )

        return cambio

    @staticmethod
    def realizar(
        db: Session,
        data: CambioCarreraCreate,
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
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

        if (
            origen.id_estudiante
            != data.id_estudiante
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La inscripción origen no pertenece "
                    "al estudiante"
                ),
            )

        if origen.estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Solo puede cambiarse de carrera "
                    "desde una inscripción activa"
                ),
            )

        carrera_ciclo_origen = (
            CatalogoAcademicoRepository
            .get_carrera_ciclo(
                db,
                origen.id_carrera_ciclo,
            )
        )

        carrera_ciclo_destino = (
            CatalogoAcademicoRepository
            .get_carrera_ciclo(
                db,
                data.id_carrera_ciclo_destino,
            )
        )

        if carrera_ciclo_destino is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Carrera/ciclo destino "
                    "no encontrada"
                ),
            )

        if not carrera_ciclo_destino.estado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La carrera/ciclo destino "
                    "está inactiva"
                ),
            )

        if (
            carrera_ciclo_origen is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La inscripción origen no posee "
                    "una carrera/ciclo válida"
                ),
            )

        # Un cambio de carrera ocurre dentro
        # del mismo ciclo escolar.
        if (
            carrera_ciclo_origen.id_ciclo
            != carrera_ciclo_destino.id_ciclo
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El cambio de carrera debe realizarse "
                    "dentro del mismo ciclo escolar"
                ),
            )

        if (
            origen.id_carrera_ciclo
            == data.id_carrera_ciclo_destino
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La carrera destino es la misma "
                    "de la inscripción actual"
                ),
            )

        ciclo = (
            CatalogoAcademicoRepository
            .get_ciclo(
                db,
                carrera_ciclo_destino.id_ciclo,
            )
        )

        if (
            ciclo is not None
            and ciclo.estado == "CERRADO"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No puede realizarse un cambio "
                    "de carrera en un ciclo cerrado"
                ),
            )

        grado = (
            CatalogoAcademicoRepository
            .get_grado(
                db,
                data.id_grado_destino,
            )
        )

        if grado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grado destino no encontrado",
            )

        if not grado.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El grado destino está inactivo",
            )

        if (
            grado.id_carrera_ciclo
            != data.id_carrera_ciclo_destino
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El grado destino no pertenece "
                    "a la carrera/ciclo seleccionada"
                ),
            )

        datos_anteriores = {
            "id_estudiante":
                data.id_estudiante,
            "id_inscripcion_origen":
                data.id_inscripcion_origen,
            "id_carrera_ciclo_origen":
                origen.id_carrera_ciclo,
            "estado_inscripcion_origen":
                origen.estado,
        }

        try:
            id_cambio = (
                CambioCarreraRepository
                .ejecutar(
                    db=db,
                    id_estudiante=
                        data.id_estudiante,
                    id_inscripcion_origen=
                        data.id_inscripcion_origen,
                    id_carrera_ciclo_destino=
                        data.id_carrera_ciclo_destino,
                    id_grado_destino=
                        data.id_grado_destino,
                    motivo=data.motivo,
                    id_usuario=id_usuario,
                )
            )

            if data.observaciones is not None:
                (
                    CambioCarreraRepository
                    .actualizar_observaciones(
                        db,
                        id_cambio,
                        data.observaciones,
                    )
                )

            cambio = CambioCarreraService.obtener(
                db,
                id_cambio,
            )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="ACADEMICO",
                accion="CAMBIO_CARRERA",
                tabla_afectada="cambio_carrera",
                id_registro=id_cambio,
                descripcion=(
                    "Cambio de carrera del estudiante "
                    f"{data.id_estudiante}"
                ),
                datos_anteriores=
                    datos_anteriores,
                datos_nuevos=cambio,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    (
                        "No fue posible realizar "
                        "el cambio de carrera"
                    ),
                ),
            )

        except Exception:
            db.rollback()
            raise

        return cambio