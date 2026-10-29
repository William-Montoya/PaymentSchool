"""Corregir calculo saldo a fecha de corte

Revision ID: 5d15b947d4ca
Revises: 8606eea8d81b
Create Date: 2026-09-21 22:40:00.362297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d15b947d4ca'
down_revision: Union[str, Sequence[str], None] = '8606eea8d81b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        r"""
        CREATE OR REPLACE FUNCTION school.fn_calcular_saldo_corte(
            p_id_inscripcion bigint,
            p_fecha_corte date
        )
        RETURNS numeric
        LANGUAGE sql
        SET search_path = school, pg_catalog
        AS $$
            SELECT COALESCE(
                SUM(
                    GREATEST(
                        (
                            o.monto_bruto

                            - COALESCE(
                                (
                                    SELECT SUM(dob.monto_aplicado)
                                    FROM descuento_obligacion dob
                                    WHERE dob.id_obligacion = o.id_obligacion
                                    AND dob.fecha_aplicacion::date <= p_fecha_corte
                                ),
                                0
                            )

                            - COALESCE(
                                (
                                    SELECT SUM(bo.monto_aplicado)
                                    FROM beca_obligacion bo
                                    WHERE bo.id_obligacion = o.id_obligacion
                                    AND bo.fecha_aplicacion::date <= p_fecha_corte
                                ),
                                0
                            )
                        )

                        - COALESCE(
                            (
                                SELECT SUM(ap.monto_aplicado)
                                FROM aplicacion_pago ap
                                JOIN pago p
                                    ON p.id_pago = ap.id_pago
                                WHERE ap.id_obligacion = o.id_obligacion
                                AND p.estado = 'CONFIRMADO'
                                AND p.fecha_pago::date <= p_fecha_corte
                            ),
                            0
                        ),
                        0
                    )
                ),
                0
            )
            FROM obligacion o
            WHERE o.id_inscripcion = p_id_inscripcion
            AND o.estado <> 'ANULADA'
            AND o.creado_en::date <= p_fecha_corte
            AND (
                o.fecha_vencimiento IS NULL
                OR o.fecha_vencimiento <= p_fecha_corte
            );
        $$;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        r"""
        CREATE OR REPLACE FUNCTION school.fn_calcular_saldo_corte(
            p_id_inscripcion bigint,
            p_fecha_corte date
        )
        RETURNS numeric
        LANGUAGE sql
        SET search_path = school, pg_catalog
        AS $$
            SELECT COALESCE(
                SUM(v.saldo),
                0
            )
            FROM vw_saldo_obligaciones v
            JOIN obligacion o
                ON o.id_obligacion = v.id_obligacion
            WHERE o.id_inscripcion = p_id_inscripcion
            AND (
                o.fecha_vencimiento IS NULL
                OR o.fecha_vencimiento <= p_fecha_corte
            );
        $$;
        """
    )
