from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.db_errors import (
    get_postgres_error_message,
)
from app.repositories.evaluacion_repository import (
    EvaluacionRepository,
)
from app.repositories.estudiante_repository import (
    EstudianteRepository,
)
from app.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from app.repositories.solvencia_repository import (
    SolvenciaRepository,
)
from app.schemas.solvencia import (
    SolvenciaGenerarCreate,
)
from app.services.auditoria_service import (
    AuditoriaService,
)


class SolvenciaService:

    @staticmethod
    def generar(
        db: Session,
        data: SolvenciaGenerarCreate,
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

        inscripcion = InscripcionRepository.get_by_id(
            db,
            data.id_inscripcion,
        )

        if inscripcion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inscripción no encontrada",
            )

        if (
            inscripcion.id_estudiante
            != data.id_estudiante
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La inscripción no pertenece "
                    "al estudiante"
                ),
            )

        evaluacion = EvaluacionRepository.get_by_id(
            db,
            data.id_evaluacion,
        )

        if evaluacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada",
            )

        if not evaluacion.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La evaluación está inactiva",
            )

        # Una misma evaluación no necesita generar
        # repetidamente nuevos certificados.
        existente = SolvenciaRepository.get_existente(
            db,
            data.id_inscripcion,
            data.id_evaluacion,
        )

        if existente is not None:
            return SolvenciaRepository.get_detalle(
                db,
                existente["id_solvencia"],
            )

        try:
            id_solvencia = (
                SolvenciaRepository.generar(
                    db=db,
                    id_estudiante=data.id_estudiante,
                    id_inscripcion=data.id_inscripcion,
                    id_evaluacion=data.id_evaluacion,
                )
            )

            solvencia = SolvenciaRepository.get_detalle(
                db,
                id_solvencia,
            )

            if solvencia is None:
                raise HTTPException(
                    status_code=
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "La solvencia fue generada, "
                        "pero no pudo recuperarse"
                    ),
                )

            AuditoriaService.registrar(
                db=db,
                id_usuario=id_usuario,
                modulo="FINANZAS",
                accion="GENERAR_SOLVENCIA",
                tabla_afectada="solvencia",
                id_registro=id_solvencia,
                descripcion=(
                    "Generación de solvencia "
                    f"para estudiante "
                    f"{data.id_estudiante}"
                ),
                datos_nuevos=solvencia,
            )

            db.commit()

        except DBAPIError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_postgres_error_message(
                    exc,
                    "No fue posible generar la solvencia",
                ),
            )

        except Exception:
            db.rollback()
            raise

        return solvencia

    @staticmethod
    def obtener(
        db: Session,
        id_solvencia: int,
    ) -> dict:

        solvencia = SolvenciaRepository.get_detalle(
            db,
            id_solvencia,
        )

        if solvencia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solvencia no encontrada",
            )

        return solvencia

    @staticmethod
    def verificar(
        db: Session,
        codigo: str,
    ) -> dict:

        solvencia = SolvenciaRepository.get_by_codigo(
            db,
            codigo,
        )

        if solvencia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Código de verificación "
                    "no encontrado"
                ),
            )

        return solvencia