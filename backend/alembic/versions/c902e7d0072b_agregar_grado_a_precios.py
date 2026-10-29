"""agregar grado a precios

Revision ID: c902e7d0072b
Revises: 5d15b947d4ca
Create Date: 2026-09-30 10:55:21.487651

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c902e7d0072b"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "5d15b947d4ca"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    op.add_column(
        "precio_carrera",
        sa.Column(
            "id_grado",
            sa.BigInteger(),
            nullable=True,
        ),
        schema="school",
    )

    op.create_foreign_key(
        "fk_precio_carrera_grado",
        "precio_carrera",
        "grado",
        ["id_grado"],
        ["id_grado"],
        source_schema="school",
        referent_schema="school",
    )

    op.create_index(
        "ix_precio_carrera_carrera_ciclo_grado_tipo",
        "precio_carrera",
        [
            "id_carrera_ciclo",
            "id_grado",
            "tipo",
        ],
        unique=False,
        schema="school",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_precio_carrera_carrera_ciclo_grado_tipo",
        table_name="precio_carrera",
        schema="school",
    )

    op.drop_constraint(
        "fk_precio_carrera_grado",
        "precio_carrera",
        type_="foreignkey",
        schema="school",
    )

    op.drop_column(
        "precio_carrera",
        "id_grado",
        schema="school",
    )