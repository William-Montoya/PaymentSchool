from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.carrera import Carrera
from app.models.carrera_ciclo import CarreraCiclo
from app.models.ciclo_escolar import CicloEscolar
from app.models.grado import Grado


class CatalogoAcademicoRepository:

    # -------------------------
    # CICLOS
    # -------------------------

    @staticmethod
    def get_ciclo(
        db: Session,
        id_ciclo: int,
    ) -> CicloEscolar | None:
        return db.get(CicloEscolar, id_ciclo)

    @staticmethod
    def get_ciclo_by_nombre(
        db: Session,
        nombre: str,
    ) -> CicloEscolar | None:
        stmt = select(CicloEscolar).where(
            CicloEscolar.nombre == nombre
        )
        return db.scalar(stmt)

    @staticmethod
    def list_ciclos(
        db: Session,
    ) -> list[CicloEscolar]:
        stmt = select(CicloEscolar).order_by(
            CicloEscolar.fecha_inicio.desc()
        )
        return list(db.scalars(stmt).all())

    # -------------------------
    # CARRERAS
    # -------------------------

    @staticmethod
    def get_carrera(
        db: Session,
        id_carrera: int,
    ) -> Carrera | None:
        return db.get(Carrera, id_carrera)

    @staticmethod
    def get_carrera_by_nombre(
        db: Session,
        nombre: str,
    ) -> Carrera | None:
        stmt = select(Carrera).where(
            Carrera.nombre == nombre
        )
        return db.scalar(stmt)

    @staticmethod
    def list_carreras(
        db: Session,
    ) -> list[Carrera]:
        stmt = select(Carrera).order_by(
            Carrera.nombre
        )
        return list(db.scalars(stmt).all())

    # -------------------------
    # CARRERA / CICLO
    # -------------------------

    @staticmethod
    def get_carrera_ciclo(
        db: Session,
        id_carrera_ciclo: int,
    ) -> CarreraCiclo | None:
        return db.get(
            CarreraCiclo,
            id_carrera_ciclo,
        )

    @staticmethod
    def get_carrera_ciclo_existente(
        db: Session,
        id_carrera: int,
        id_ciclo: int,
    ) -> CarreraCiclo | None:
        stmt = select(CarreraCiclo).where(
            CarreraCiclo.id_carrera == id_carrera,
            CarreraCiclo.id_ciclo == id_ciclo,
        )
        return db.scalar(stmt)

    @staticmethod
    def list_carrera_ciclos(
        db: Session,
        id_ciclo: int | None = None,
        id_carrera: int | None = None,
    ) -> list[CarreraCiclo]:

        stmt = select(CarreraCiclo)

        if id_ciclo is not None:
            stmt = stmt.where(
                CarreraCiclo.id_ciclo == id_ciclo
            )

        if id_carrera is not None:
            stmt = stmt.where(
                CarreraCiclo.id_carrera == id_carrera
            )

        stmt = stmt.order_by(
            CarreraCiclo.id_ciclo.desc(),
            CarreraCiclo.id_carrera,
        )

        return list(db.scalars(stmt).all())

    # -------------------------
    # GRADOS
    # -------------------------

    @staticmethod
    def get_grado(
        db: Session,
        id_grado: int,
    ) -> Grado | None:
        return db.get(Grado, id_grado)

    @staticmethod
    def get_grado_by_nombre(
        db: Session,
        id_carrera_ciclo: int,
        nombre: str,
    ) -> Grado | None:

        stmt = select(Grado).where(
            Grado.id_carrera_ciclo
            == id_carrera_ciclo,
            Grado.nombre == nombre,
        )

        return db.scalar(stmt)

    @staticmethod
    def list_grados(
        db: Session,
        id_carrera_ciclo: int | None = None,
    ) -> list[Grado]:

        stmt = select(Grado)

        if id_carrera_ciclo is not None:
            stmt = stmt.where(
                Grado.id_carrera_ciclo
                == id_carrera_ciclo
            )

        stmt = stmt.order_by(
            Grado.id_carrera_ciclo,
            Grado.nivel_orden,
            Grado.nombre,
        )

        return list(db.scalars(stmt).all())