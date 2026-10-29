"""codigo estudiante automatico

Revision ID: f81b73c9a426
Revises: db6b8bc8d5c4
Create Date: 2026-10-02
"""

from alembic import op


revision = "f81b73c9a426"
down_revision = "db6b8bc8d5c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE SEQUENCE
            school.seq_codigo_estudiante
        AS BIGINT
        START WITH 1
        INCREMENT BY 1
        MINVALUE 1
        NO MAXVALUE
        CACHE 1
        """
    )

    op.execute(
        """
        SELECT setval(
            'school.seq_codigo_estudiante',
            GREATEST(
                COALESCE(
                    (
                        SELECT MAX(
                            CAST(
                                SUBSTRING(
                                    codigo_estudiante
                                    FROM '^EST-([0-9]+)$'
                                )
                                AS BIGINT
                            )
                        )
                        FROM school.estudiante
                        WHERE codigo_estudiante
                              ~ '^EST-[0-9]+$'
                    ),
                    0
                ),
                COALESCE(
                    (
                        SELECT MAX(id_estudiante)
                        FROM school.estudiante
                    ),
                    0
                )
            ) + 1,
            false
        )
        """
    )

    op.execute(
        """
        ALTER TABLE school.estudiante
        ALTER COLUMN codigo_estudiante
        SET DEFAULT (
            'EST-' ||
            LPAD(
                nextval(
                    'school.seq_codigo_estudiante'
                )::text,
                6,
                '0'
            )
        )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE school.estudiante
        ALTER COLUMN codigo_estudiante
        DROP DEFAULT
        """
    )

    op.execute(
        """
        DROP SEQUENCE
        school.seq_codigo_estudiante
        """
    )