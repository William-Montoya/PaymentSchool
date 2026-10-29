from sqlalchemy import text
from sqlalchemy.orm import Session


class ReciboRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        id_recibo: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    id_recibo,
                    id_pago,
                    numero_recibo,
                    codigo_verificacion,
                    fecha_emision

                FROM school.recibo

                WHERE id_recibo = :id_recibo
                """
            ),
            {
                "id_recibo": id_recibo,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def get_by_pago(
        db: Session,
        id_pago: int,
    ) -> dict | None:

        row = db.execute(
            text(
                """
                SELECT
                    id_recibo,
                    id_pago,
                    numero_recibo,
                    codigo_verificacion,
                    fecha_emision

                FROM school.recibo

                WHERE id_pago = :id_pago
                """
            ),
            {
                "id_pago": id_pago,
            },
        ).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def generar(
        db: Session,
        id_pago: int,
    ) -> int:

        return db.scalar(
            text(
                """
                SELECT school.fn_generar_recibo(
                    :id_pago
                )
                """
            ),
            {
                "id_pago": id_pago,
            },
        )