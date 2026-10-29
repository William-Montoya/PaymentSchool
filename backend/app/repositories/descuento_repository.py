from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.descuento import Descuento
from app.models.descuento_obligacion import (
    DescuentoObligacion,
)
from app.models.obligacion import Obligacion


class DescuentoRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_descuento: int,
    ) -> Descuento | None:

        return db.get(
            Descuento,
            id_descuento,
        )

    @staticmethod
    def get_by_nombre(
        db: Session,
        nombre: str,
    ) -> Descuento | None:

        stmt = select(Descuento).where(
            Descuento.nombre == nombre
        )

        return db.scalar(stmt)

    @staticmethod
    def list(
        db: Session,
        activo: bool | None = None,
    ) -> list[Descuento]:

        stmt = select(Descuento)

        if activo is not None:
            stmt = stmt.where(
                Descuento.activo == activo
            )

        stmt = stmt.order_by(
            Descuento.nombre
        )

        return list(
            db.scalars(stmt).all()
        )

    @staticmethod
    def get_aplicacion_existente(
        db: Session,
        id_descuento: int,
        id_obligacion: int,
    ) -> DescuentoObligacion | None:

        stmt = select(
            DescuentoObligacion
        ).where(
            DescuentoObligacion.id_descuento
            == id_descuento,

            DescuentoObligacion.id_obligacion
            == id_obligacion,
        )

        return db.scalar(stmt)

    @staticmethod
    def aplicar(
        db: Session,
        id_descuento: int,
        id_obligacion: int,
    ) -> None:

        db.execute(
            text(
                """
                SELECT
                    school.fn_aplicar_descuento_obligacion(
                        :id_obligacion,
                        :id_descuento
                    )
                """
            ),
            {
                "id_obligacion": id_obligacion,
                "id_descuento": id_descuento,
            },
        )

    @staticmethod
    def list_aplicaciones(
        db: Session,
        id_obligacion: int | None = None,
        id_descuento: int | None = None,
    ) -> list[dict]:

        stmt = (
            select(
                DescuentoObligacion
                .id_descuento_obligacion,

                DescuentoObligacion.id_descuento,

                Descuento.nombre.label(
                    "descuento"
                ),

                DescuentoObligacion.id_obligacion,

                Obligacion.concepto.label(
                    "concepto"
                ),

                DescuentoObligacion.monto_aplicado,
                DescuentoObligacion.fecha_aplicacion,
            )
            .join(
                Descuento,
                Descuento.id_descuento
                == DescuentoObligacion.id_descuento,
            )
            .join(
                Obligacion,
                Obligacion.id_obligacion
                == DescuentoObligacion.id_obligacion,
            )
        )

        if id_obligacion is not None:
            stmt = stmt.where(
                DescuentoObligacion.id_obligacion
                == id_obligacion
            )

        if id_descuento is not None:
            stmt = stmt.where(
                DescuentoObligacion.id_descuento
                == id_descuento
            )

        stmt = stmt.order_by(
            DescuentoObligacion
            .fecha_aplicacion.desc()
        )

        rows = db.execute(
            stmt
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]