"""validar grado en mensualidades

Revision ID: db6b8bc8d5c4
Revises: c902e7d0072b
Create Date: 2026-09-30 14:29:02.729912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db6b8bc8d5c4'
down_revision: Union[str, Sequence[str], None] = 'c902e7d0072b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION school.fn_generar_obligaciones_mensuales(
            p_id_inscripcion bigint,
            p_id_precio bigint,
            p_fecha_inicio date,
            p_cantidad_meses integer
        )
        RETURNS void
        LANGUAGE plpgsql
        SET search_path TO 'school', 'pg_catalog'
        AS $function$
        DECLARE
            v_monto NUMERIC(12,2);

            v_fecha DATE;

            v_contador INTEGER;

            v_periodo VARCHAR(20);

            v_carrera_ciclo_precio BIGINT;
            v_carrera_ciclo_inscripcion BIGINT;

            v_grado_precio BIGINT;
            v_grado_inscripcion BIGINT;
        BEGIN

            IF p_cantidad_meses IS NULL
               OR p_cantidad_meses <= 0 THEN
                RAISE EXCEPTION
                    'La cantidad de meses debe ser mayor a cero.';
            END IF;

            IF p_fecha_inicio IS NULL THEN
                RAISE EXCEPTION
                    'La fecha de inicio es obligatoria.';
            END IF;

            SELECT
                monto,
                id_carrera_ciclo,
                id_grado
            INTO
                v_monto,
                v_carrera_ciclo_precio,
                v_grado_precio
            FROM precio_carrera
            WHERE id_precio = p_id_precio
              AND tipo = 'MENSUALIDAD'
              AND activo = TRUE;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'No existe un precio de mensualidad activo.';
            END IF;

            SELECT
                id_carrera_ciclo,
                id_grado
            INTO
                v_carrera_ciclo_inscripcion,
                v_grado_inscripcion
            FROM inscripcion
            WHERE id_inscripcion = p_id_inscripcion;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'La inscripción no existe.';
            END IF;

            IF (
                v_carrera_ciclo_precio
                <> v_carrera_ciclo_inscripcion
            ) THEN
                RAISE EXCEPTION
                    'El precio de mensualidad no pertenece a la carrera/ciclo de la inscripción.';
            END IF;

            IF (
                v_grado_precio
                IS DISTINCT FROM
                v_grado_inscripcion
            ) THEN
                RAISE EXCEPTION
                    'El precio de mensualidad no pertenece al grado de la inscripción.';
            END IF;

            FOR v_contador IN
                0..(p_cantidad_meses - 1)
            LOOP

                v_fecha :=
                    p_fecha_inicio
                    + (
                        v_contador || ' month'
                    )::INTERVAL;

                v_periodo :=
                    TO_CHAR(
                        v_fecha,
                        'YYYY-MM'
                    );

                INSERT INTO obligacion (
                    id_inscripcion,
                    id_precio,
                    concepto,
                    periodo,
                    fecha_vencimiento,
                    monto_bruto,
                    monto_neto,
                    estado,
                    tipo_obligacion
                )
                VALUES (
                    p_id_inscripcion,
                    p_id_precio,
                    'Mensualidad',
                    v_periodo,
                    v_fecha,
                    v_monto,
                    v_monto,
                    'PENDIENTE',
                    'MENSUALIDAD'
                );

            END LOOP;

        END;
        $function$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION school.fn_generar_obligaciones_mensuales(
            p_id_inscripcion bigint,
            p_id_precio bigint,
            p_fecha_inicio date,
            p_cantidad_meses integer
        )
        RETURNS void
        LANGUAGE plpgsql
        SET search_path TO 'school', 'pg_catalog'
        AS $function$
        DECLARE
            v_monto NUMERIC(12,2);

            v_fecha DATE;

            v_contador INTEGER;

            v_periodo VARCHAR(20);

            v_carrera_ciclo_precio BIGINT;
            v_carrera_ciclo_inscripcion BIGINT;
        BEGIN

            IF p_cantidad_meses IS NULL
               OR p_cantidad_meses <= 0 THEN
                RAISE EXCEPTION
                    'La cantidad de meses debe ser mayor a cero.';
            END IF;

            IF p_fecha_inicio IS NULL THEN
                RAISE EXCEPTION
                    'La fecha de inicio es obligatoria.';
            END IF;

            SELECT
                monto,
                id_carrera_ciclo
            INTO
                v_monto,
                v_carrera_ciclo_precio
            FROM precio_carrera
            WHERE id_precio = p_id_precio
              AND tipo = 'MENSUALIDAD'
              AND activo = TRUE;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'No existe un precio de mensualidad activo.';
            END IF;

            SELECT
                id_carrera_ciclo
            INTO
                v_carrera_ciclo_inscripcion
            FROM inscripcion
            WHERE id_inscripcion = p_id_inscripcion;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'La inscripción no existe.';
            END IF;

            IF (
                v_carrera_ciclo_precio
                <> v_carrera_ciclo_inscripcion
            ) THEN
                RAISE EXCEPTION
                    'El precio de mensualidad no pertenece a la carrera/ciclo de la inscripción.';
            END IF;

            FOR v_contador IN
                0..(p_cantidad_meses - 1)
            LOOP

                v_fecha :=
                    p_fecha_inicio
                    + (
                        v_contador || ' month'
                    )::INTERVAL;

                v_periodo :=
                    TO_CHAR(
                        v_fecha,
                        'YYYY-MM'
                    );

                INSERT INTO obligacion (
                    id_inscripcion,
                    id_precio,
                    concepto,
                    periodo,
                    fecha_vencimiento,
                    monto_bruto,
                    monto_neto,
                    estado,
                    tipo_obligacion
                )
                VALUES (
                    p_id_inscripcion,
                    p_id_precio,
                    'Mensualidad',
                    v_periodo,
                    v_fecha,
                    v_monto,
                    v_monto,
                    'PENDIENTE',
                    'MENSUALIDAD'
                );

            END LOOP;

        END;
        $function$;
        """
    )