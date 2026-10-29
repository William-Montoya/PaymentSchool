from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.carrera import Carrera
from app.models.carrera_ciclo import CarreraCiclo
from app.models.ciclo_escolar import CicloEscolar
from app.models.estudiante import Estudiante
from app.models.grado import Grado
from app.models.inscripcion import Inscripcion


class InscripcionRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_inscripcion: int,
    ) -> Inscripcion | None:
        return db.get(
            Inscripcion,
            id_inscripcion,
        )

    @staticmethod
    def get_activa_en_ciclo(
        db: Session,
        id_estudiante: int,
        id_ciclo: int,
    ) -> Inscripcion | None:

        stmt = (
            select(Inscripcion)
            .join(
                CarreraCiclo,
                CarreraCiclo.id_carrera_ciclo
                == Inscripcion.id_carrera_ciclo,
            )
            .where(
                Inscripcion.id_estudiante
                == id_estudiante,
                CarreraCiclo.id_ciclo
                == id_ciclo,
                Inscripcion.estado == "ACTIVA",
            )
        )

        return db.scalar(stmt)

    @staticmethod
    def _detalle_stmt():

        return (
            select(
                Inscripcion.id_inscripcion,
                Inscripcion.id_estudiante,
                Inscripcion.id_carrera_ciclo,
                Inscripcion.id_grado,
                Inscripcion.fecha_inscripcion,
                Inscripcion.tipo,
                Inscripcion.estado,
                Inscripcion.observaciones,
                Inscripcion.creado_en,

                Estudiante.codigo_estudiante.label(
                    "codigo_estudiante"
                ),

                func.concat(
                    Estudiante.nombres,
                    " ",
                    Estudiante.apellidos,
                ).label("estudiante"),

                Carrera.nombre.label("carrera"),
                CicloEscolar.nombre.label("ciclo"),
                Grado.nombre.label("grado"),
            )
            .join(
                Estudiante,
                Estudiante.id_estudiante
                == Inscripcion.id_estudiante,
            )
            .join(
                CarreraCiclo,
                CarreraCiclo.id_carrera_ciclo
                == Inscripcion.id_carrera_ciclo,
            )
            .join(
                Carrera,
                Carrera.id_carrera
                == CarreraCiclo.id_carrera,
            )
            .join(
                CicloEscolar,
                CicloEscolar.id_ciclo
                == CarreraCiclo.id_ciclo,
            )
            .join(
                Grado,
                Grado.id_grado
                == Inscripcion.id_grado,
            )
        )

    @staticmethod
    def get_detalle(
        db: Session,
        id_inscripcion: int,
    ) -> dict | None:

        stmt = (
            InscripcionRepository
            ._detalle_stmt()
            .where(
                Inscripcion.id_inscripcion
                == id_inscripcion
            )
        )

        row = db.execute(
            stmt
        ).first()

        if row is None:
            return None

        return dict(
            row._mapping
        )

    @staticmethod
    def list_detalle(
        db: Session,
        id_estudiante: int | None = None,
        id_ciclo: int | None = None,
        id_carrera: int | None = None,
        estado: str | None = None,
        buscar: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:

        stmt = (
            InscripcionRepository
            ._detalle_stmt()
        )

        if id_estudiante is not None:
            stmt = stmt.where(
                Inscripcion.id_estudiante
                == id_estudiante
            )

        if id_ciclo is not None:
            stmt = stmt.where(
                CarreraCiclo.id_ciclo
                == id_ciclo
            )

        if id_carrera is not None:
            stmt = stmt.where(
                CarreraCiclo.id_carrera
                == id_carrera
            )

        if estado is not None:
            stmt = stmt.where(
                Inscripcion.estado
                == estado
            )

        if buscar:
            patron = (
                f"%{buscar.strip()}%"
            )

            nombre_completo = func.concat(
                Estudiante.nombres,
                " ",
                Estudiante.apellidos,
            )

            stmt = stmt.where(
                or_(
                    Estudiante
                    .codigo_estudiante
                    .ilike(patron),

                    Estudiante
                    .nombres
                    .ilike(patron),

                    Estudiante
                    .apellidos
                    .ilike(patron),

                    nombre_completo
                    .ilike(patron),

                    Estudiante
                    .cui
                    .ilike(patron),

                    Carrera
                    .nombre
                    .ilike(patron),

                    CicloEscolar
                    .nombre
                    .ilike(patron),

                    Grado
                    .nombre
                    .ilike(patron),
                )
            )

        stmt = stmt.order_by(
            Inscripcion
            .fecha_inscripcion
            .desc(),

            Inscripcion
            .id_inscripcion
            .desc(),
        )

        if limit is not None:
            stmt = stmt.limit(
                limit
            )

        rows = (
            db.execute(
                stmt
            )
            .all()
        )

        return [
            dict(
                row._mapping
            )
            for row in rows
        ]