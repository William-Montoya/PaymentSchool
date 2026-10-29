"""Objetos PostgreSQL PaymentSchool

Revision ID: 333af9205c0a
Revises: fb277a875945

Reconstruye la lógica PostgreSQL que no administra autogenerate:
- 23 funciones
- 7 triggers
- 6 vistas

Incluye correcciones de integridad detectadas al comparar el dump original:
- tipo_obligacion en generación de mensualidades
- aplicaciones de pagos anulados excluidas del reparto automático
- obligaciones ANULADA no generan deuda ni pierden su estado al recalcular
- recálculo de OLD/NEW al mover una aplicación entre obligaciones
- bloqueo de pago/obligación al validar aplicaciones concurrentes
- coherencia estudiante/inscripción/ciclo al generar solvencia
"""

from typing import Sequence, Union

from alembic import op

revision: str = "333af9205c0a"
down_revision: Union[str, Sequence[str], None] = "fb277a875945"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _exec(sql: str) -> None:
    # exec_driver_sql evita que SQLAlchemy interprete los casts PostgreSQL ::tipo
    # como parámetros enlazados dentro del DDL de funciones/vistas.
    op.get_bind().exec_driver_sql(sql)


def upgrade() -> None:
    _exec("SET LOCAL search_path TO school, pg_catalog")
    # Vista base usada por funciones y por el resto de reportes financieros.
    _exec(r'''
CREATE OR REPLACE VIEW school.vw_saldo_obligaciones AS
 SELECT o.id_obligacion,
    o.id_inscripcion,
    o.concepto,
    o.periodo,
    o.fecha_vencimiento,
    o.monto_bruto,
    o.monto_descuento,
    o.monto_beca,
    o.monto_neto,
    COALESCE(sum(
        CASE
            WHEN (p.estado = 'CONFIRMADO'::school.estado_pago) THEN ap.monto_aplicado
            ELSE (0)::numeric
        END), (0)::numeric) AS total_pagado,
    CASE
        WHEN o.estado = 'ANULADA'::school.estado_obligacion THEN (0)::numeric
        ELSE (o.monto_neto - COALESCE(sum(
            CASE
                WHEN (p.estado = 'CONFIRMADO'::school.estado_pago) THEN ap.monto_aplicado
                ELSE (0)::numeric
            END), (0)::numeric))
    END AS saldo
   FROM ((school.obligacion o
     LEFT JOIN school.aplicacion_pago ap ON ((ap.id_obligacion = o.id_obligacion)))
     LEFT JOIN school.pago p ON ((p.id_pago = ap.id_pago)))
  GROUP BY o.id_obligacion;
''')
    # Funciones de negocio, validación y soporte de triggers.
    # fn_actualizar_estado_obligacion
    _exec(r'''
CREATE FUNCTION school.fn_actualizar_estado_obligacion(p_id_obligacion bigint) RETURNS void
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_neto NUMERIC(12,2);
    v_pagado NUMERIC(12,2);
BEGIN

    SELECT monto_neto
    INTO v_neto
    FROM obligacion
    WHERE id_obligacion = p_id_obligacion;

    SELECT COALESCE(SUM(ap.monto_aplicado), 0)
    INTO v_pagado
    FROM aplicacion_pago ap
    JOIN pago p
        ON p.id_pago = ap.id_pago
    WHERE ap.id_obligacion = p_id_obligacion
      AND p.estado = 'CONFIRMADO';

    UPDATE obligacion
    SET estado =
        CASE
            WHEN v_pagado <= 0 THEN 'PENDIENTE'::estado_obligacion

            WHEN v_pagado < v_neto THEN 'PARCIAL'::estado_obligacion

            WHEN v_pagado >= v_neto THEN 'PAGADA'::estado_obligacion
        END
    WHERE id_obligacion = p_id_obligacion
      AND estado <> 'ANULADA'::estado_obligacion;

END;
$$;
''')
    # fn_anular_pago
    _exec(r'''
CREATE FUNCTION school.fn_anular_pago(p_id_pago bigint, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS void
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_estado estado_pago;
BEGIN

    SELECT estado
    INTO v_estado
    FROM pago
    WHERE id_pago = p_id_pago;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'El pago no existe.';
    END IF;

    IF v_estado = 'ANULADO' THEN
        RAISE EXCEPTION
            'El pago ya se encuentra anulado.';
    END IF;

    UPDATE pago
    SET
        estado = 'ANULADO',

        observaciones =
            COALESCE(observaciones, '')
            || ' | ANULADO: '
            || p_motivo

    WHERE id_pago = p_id_pago;

    UPDATE saldo_favor
    SET
        estado = 'ANULADO',
        monto_disponible = 0
    WHERE id_pago_origen = p_id_pago;

END;
$$;
''')
    # fn_aplicar_beca_obligacion
    _exec(r'''
CREATE FUNCTION school.fn_aplicar_beca_obligacion(p_id_obligacion bigint, p_porcentaje numeric) RETURNS void
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_monto_bruto NUMERIC(12,2);
    v_monto_beca NUMERIC(12,2);
BEGIN

    IF p_porcentaje < 0 OR p_porcentaje > 100 THEN
        RAISE EXCEPTION
            'El porcentaje debe estar entre 0 y 100.';
    END IF;

    SELECT monto_bruto
    INTO v_monto_bruto
    FROM obligacion
    WHERE id_obligacion = p_id_obligacion;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'La obligación no existe.';
    END IF;

    v_monto_beca :=
        ROUND(
            v_monto_bruto * p_porcentaje / 100,
            2
        );

    UPDATE obligacion
    SET
        monto_beca = v_monto_beca,

        monto_neto =
            monto_bruto
            - monto_descuento
            - v_monto_beca

    WHERE id_obligacion = p_id_obligacion;

END;
$$;
''')
    # fn_aplicar_descuento_obligacion
    _exec(r'''
CREATE FUNCTION school.fn_aplicar_descuento_obligacion(p_id_obligacion bigint, p_id_descuento bigint) RETURNS void
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_porcentaje NUMERIC(5,2);
    v_monto_fijo NUMERIC(12,2);

    v_monto_bruto NUMERIC(12,2);

    v_descuento NUMERIC(12,2);
BEGIN

    SELECT
        porcentaje,
        monto_fijo
    INTO
        v_porcentaje,
        v_monto_fijo
    FROM descuento
    WHERE id_descuento = p_id_descuento
      AND activo = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'El descuento no existe o está inactivo.';
    END IF;

    SELECT monto_bruto
    INTO v_monto_bruto
    FROM obligacion
    WHERE id_obligacion = p_id_obligacion;

    IF v_porcentaje IS NOT NULL THEN

        v_descuento :=
            ROUND(
                v_monto_bruto * v_porcentaje / 100,
                2
            );

    ELSE

        v_descuento := v_monto_fijo;

    END IF;

    INSERT INTO descuento_obligacion (
        id_descuento,
        id_obligacion,
        monto_aplicado
    )
    VALUES (
        p_id_descuento,
        p_id_obligacion,
        v_descuento
    );

    UPDATE obligacion
    SET
        monto_descuento =
            monto_descuento + v_descuento,

        monto_neto =
            monto_bruto
            - monto_beca
            - (monto_descuento + v_descuento)

    WHERE id_obligacion = p_id_obligacion;

END;
$$;
''')
    # fn_saldo_disponible_pago
    _exec(r'''
CREATE FUNCTION school.fn_saldo_disponible_pago(p_id_pago bigint) RETURNS numeric
    LANGUAGE sql
    SET search_path = school, pg_catalog
    AS $$
    SELECT
        p.monto_total
        -
        COALESCE(
            (
                SELECT SUM(ap.monto_aplicado)
                FROM aplicacion_pago ap
                WHERE ap.id_pago = p.id_pago
            ),
            0
        )
    FROM pago p
    WHERE p.id_pago = p_id_pago
      AND p.estado = 'CONFIRMADO';
$$;
''')
    # fn_aplicar_pago
    _exec(r'''
CREATE FUNCTION school.fn_aplicar_pago(p_id_pago bigint, p_id_obligacion bigint, p_monto numeric) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_id_aplicacion BIGINT;
    v_saldo_pago NUMERIC(12,2);
BEGIN

    IF p_monto <= 0 THEN
        RAISE EXCEPTION
            'El monto a aplicar debe ser mayor a cero.';
    END IF;

    v_saldo_pago :=
        fn_saldo_disponible_pago(p_id_pago);

    IF v_saldo_pago IS NULL THEN
        RAISE EXCEPTION
            'El pago no existe o no está confirmado.';
    END IF;

    IF p_monto > v_saldo_pago THEN
        RAISE EXCEPTION
            'El monto excede el saldo disponible del pago.';
    END IF;

    INSERT INTO aplicacion_pago (
        id_pago,
        id_obligacion,
        monto_aplicado
    )
    VALUES (
        p_id_pago,
        p_id_obligacion,
        p_monto
    )
    RETURNING id_aplicacion
    INTO v_id_aplicacion;

    RETURN v_id_aplicacion;
END;
$$;
''')
    # fn_aplicar_saldo_favor
    _exec(r'''
CREATE FUNCTION school.fn_aplicar_saldo_favor(p_id_saldo_favor bigint, p_id_obligacion bigint, p_monto numeric) RETURNS void
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_estudiante_saldo BIGINT;
    v_estudiante_obligacion BIGINT;

    v_disponible NUMERIC(12,2);

    v_pago_origen BIGINT;
BEGIN

    SELECT
        id_estudiante,
        monto_disponible,
        id_pago_origen
    INTO
        v_estudiante_saldo,
        v_disponible,
        v_pago_origen
    FROM saldo_favor
    WHERE id_saldo_favor = p_id_saldo_favor
      AND estado = 'ACTIVO';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'El saldo a favor no existe o no está activo.';
    END IF;

    SELECT i.id_estudiante
    INTO v_estudiante_obligacion
    FROM obligacion o
    JOIN inscripcion i
        ON i.id_inscripcion = o.id_inscripcion
    WHERE o.id_obligacion = p_id_obligacion;

    IF v_estudiante_saldo <> v_estudiante_obligacion THEN
        RAISE EXCEPTION
            'El saldo a favor pertenece a otro estudiante.';
    END IF;

    IF p_monto > v_disponible THEN
        RAISE EXCEPTION
            'El monto excede el saldo disponible.';
    END IF;

    PERFORM fn_aplicar_pago(
        v_pago_origen,
        p_id_obligacion,
        p_monto
    );

    UPDATE saldo_favor
    SET
        monto_disponible =
            monto_disponible - p_monto,

        estado =
            CASE
                WHEN monto_disponible - p_monto <= 0
                THEN 'AGOTADO'
                ELSE 'ACTIVO'
            END
    WHERE id_saldo_favor = p_id_saldo_favor;

END;
$$;
''')
    # fn_calcular_saldo_corte
    _exec(r'''
CREATE FUNCTION school.fn_calcular_saldo_corte(p_id_inscripcion bigint, p_fecha_corte date) RETURNS numeric
    LANGUAGE sql
    SET search_path = school, pg_catalog
    AS $$
    SELECT COALESCE(
        SUM(
            v.saldo
        ),
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
''')
    # fn_cambiar_carrera
    _exec(r'''
CREATE FUNCTION school.fn_cambiar_carrera(p_id_estudiante bigint, p_id_inscripcion_origen bigint, p_id_carrera_ciclo_destino bigint, p_id_grado_destino bigint, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_id_inscripcion_destino BIGINT;
    v_id_cambio BIGINT;

    v_estudiante_origen BIGINT;
BEGIN

    -- Bloquear inscripción para evitar operaciones simultáneas

    SELECT id_estudiante
    INTO v_estudiante_origen
    FROM inscripcion
    WHERE id_inscripcion = p_id_inscripcion_origen
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'La inscripción origen no existe.';
    END IF;

    IF v_estudiante_origen <> p_id_estudiante THEN
        RAISE EXCEPTION
            'La inscripción no pertenece al estudiante.';
    END IF;


    -- Crear nueva inscripción

    INSERT INTO inscripcion (
        id_estudiante,
        id_carrera_ciclo,
        id_grado,
        fecha_inscripcion,
        tipo,
        estado,
        observaciones
    )
    VALUES (
        p_id_estudiante,
        p_id_carrera_ciclo_destino,
        p_id_grado_destino,
        CURRENT_DATE,
        'TRASLADO',
        'ACTIVA',
        'Generada por cambio de carrera'
    )
    RETURNING id_inscripcion
    INTO v_id_inscripcion_destino;


    -- Registrar cambio

    INSERT INTO cambio_carrera (
        id_estudiante,
        id_inscripcion_origen,
        id_inscripcion_destino,
        fecha_aprobacion,
        motivo,
        estado,
        id_usuario
    )
    VALUES (
        p_id_estudiante,
        p_id_inscripcion_origen,
        v_id_inscripcion_destino,
        CURRENT_TIMESTAMP,
        p_motivo,
        'APROBADO',
        p_id_usuario
    )
    RETURNING id_cambio
    INTO v_id_cambio;


    -- Finalizar inscripción anterior

    UPDATE inscripcion
    SET estado = 'FINALIZADA'
    WHERE id_inscripcion = p_id_inscripcion_origen;


    RETURN v_id_cambio;

END;
$$;
''')
    # fn_generar_obligaciones_mensuales
    _exec(r'''
CREATE FUNCTION school.fn_generar_obligaciones_mensuales(p_id_inscripcion bigint, p_id_precio bigint, p_fecha_inicio date, p_cantidad_meses integer) RETURNS void
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_monto NUMERIC(12,2);

    v_fecha DATE;

    v_contador INTEGER;

    v_periodo VARCHAR(20);

    v_carrera_ciclo_precio BIGINT;
    v_carrera_ciclo_inscripcion BIGINT;
BEGIN

    IF p_cantidad_meses IS NULL OR p_cantidad_meses <= 0 THEN
        RAISE EXCEPTION
            'La cantidad de meses debe ser mayor a cero.';
    END IF;

    IF p_fecha_inicio IS NULL THEN
        RAISE EXCEPTION
            'La fecha de inicio es obligatoria.';
    END IF;

    SELECT monto, id_carrera_ciclo
    INTO v_monto, v_carrera_ciclo_precio
    FROM precio_carrera
    WHERE id_precio = p_id_precio
      AND tipo = 'MENSUALIDAD'
      AND activo = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No existe un precio de mensualidad activo.';
    END IF;

    SELECT id_carrera_ciclo
    INTO v_carrera_ciclo_inscripcion
    FROM inscripcion
    WHERE id_inscripcion = p_id_inscripcion;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'La inscripción no existe.';
    END IF;

    IF v_carrera_ciclo_precio <> v_carrera_ciclo_inscripcion THEN
        RAISE EXCEPTION
            'El precio de mensualidad no pertenece a la carrera/ciclo de la inscripción.';
    END IF;

    FOR v_contador IN 0..(p_cantidad_meses - 1)
    LOOP

        v_fecha :=
            p_fecha_inicio
            + (v_contador || ' month')::INTERVAL;

        v_periodo :=
            TO_CHAR(v_fecha, 'YYYY-MM');

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
$$;
''')
    # fn_generar_recibo
    _exec(r'''
CREATE FUNCTION school.fn_generar_recibo(p_id_pago bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_numero_recibo VARCHAR(50);
    v_codigo VARCHAR(100);

    v_id_recibo BIGINT;
BEGIN

    v_numero_recibo :=
        'REC-'
        || TO_CHAR(
            CURRENT_TIMESTAMP,
            'YYYY'
        )
        || '-'
        || LPAD(
            p_id_pago::TEXT,
            8,
            '0'
        );

    v_codigo :=
        'VER-'
        || MD5(
            p_id_pago::TEXT
            || CURRENT_TIMESTAMP::TEXT
            || RANDOM()::TEXT
        );

    INSERT INTO recibo (
        id_pago,
        numero_recibo,
        codigo_verificacion
    )
    VALUES (
        p_id_pago,
        v_numero_recibo,
        v_codigo
    )
    RETURNING id_recibo
    INTO v_id_recibo;

    RETURN v_id_recibo;
END;
$$;
''')
    # fn_generar_solvencia
    _exec(r'''
CREATE FUNCTION school.fn_generar_solvencia(p_id_estudiante bigint, p_id_inscripcion bigint, p_id_evaluacion bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_fecha_corte DATE;
    v_saldo NUMERIC(12,2);
    v_estado estado_solvencia;
    v_codigo VARCHAR(100);
    v_id BIGINT;
    v_id_ciclo_inscripcion BIGINT;
    v_id_ciclo_evaluacion BIGINT;
    v_id_estudiante_inscripcion BIGINT;
BEGIN

    SELECT
        i.id_estudiante,
        cc.id_ciclo
    INTO
        v_id_estudiante_inscripcion,
        v_id_ciclo_inscripcion
    FROM inscripcion i
    JOIN carrera_ciclo cc
        ON cc.id_carrera_ciclo = i.id_carrera_ciclo
    WHERE i.id_inscripcion = p_id_inscripcion;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'La inscripción no existe.';
    END IF;

    IF v_id_estudiante_inscripcion <> p_id_estudiante THEN
        RAISE EXCEPTION
            'La inscripción no pertenece al estudiante.';
    END IF;

    SELECT
        fecha_corte_finanzas,
        id_ciclo
    INTO
        v_fecha_corte,
        v_id_ciclo_evaluacion
    FROM evaluacion
    WHERE id_evaluacion = p_id_evaluacion;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'La evaluación no existe.';
    END IF;

    IF v_id_ciclo_evaluacion <> v_id_ciclo_inscripcion THEN
        RAISE EXCEPTION
            'La evaluación no pertenece al ciclo de la inscripción.';
    END IF;

    v_saldo :=
        fn_calcular_saldo_corte(
            p_id_inscripcion,
            v_fecha_corte
        );

    IF v_saldo <= 0 THEN
        v_estado := 'SOLVENTE';
    ELSE
        v_estado := 'INSOLVENTE';
    END IF;

    v_codigo :=
        'SOL-' ||
        TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISS') ||
        '-' ||
        LPAD(
            FLOOR(RANDOM() * 100000)::TEXT,
            5,
            '0'
        );

    INSERT INTO solvencia (
        id_estudiante,
        id_inscripcion,
        id_evaluacion,
        fecha_corte,
        saldo_corte,
        estado,
        codigo_verificacion
    )
    VALUES (
        p_id_estudiante,
        p_id_inscripcion,
        p_id_evaluacion,
        v_fecha_corte,
        GREATEST(v_saldo, 0),
        v_estado,
        v_codigo
    )
    RETURNING id_solvencia
    INTO v_id;

    RETURN v_id;

END;
$$;
''')
    # fn_recalcular_obligaciones_pago_anulado
    _exec(r'''
CREATE FUNCTION school.fn_recalcular_obligaciones_pago_anulado() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_aplicacion RECORD;
BEGIN

    IF OLD.estado <> NEW.estado
       AND NEW.estado = 'ANULADO'
    THEN

        FOR v_aplicacion IN

            SELECT id_obligacion
            FROM aplicacion_pago
            WHERE id_pago = NEW.id_pago

        LOOP

            PERFORM fn_actualizar_estado_obligacion(
                v_aplicacion.id_obligacion
            );

        END LOOP;

    END IF;

    RETURN NEW;
END;
$$;
''')
    # fn_registrar_auditoria
    _exec(r'''
CREATE FUNCTION school.fn_registrar_auditoria(p_id_usuario bigint, p_modulo character varying, p_accion character varying, p_tabla character varying, p_id_registro bigint, p_descripcion text, p_datos_anteriores jsonb DEFAULT NULL::jsonb, p_datos_nuevos jsonb DEFAULT NULL::jsonb) RETURNS void
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
BEGIN

    INSERT INTO auditoria (
        id_usuario,
        modulo,
        accion,
        tabla_afectada,
        id_registro,
        descripcion,
        datos_anteriores,
        datos_nuevos
    )
    VALUES (
        p_id_usuario,
        p_modulo,
        p_accion,
        p_tabla,
        p_id_registro,
        p_descripcion,
        p_datos_anteriores,
        p_datos_nuevos
    );

END;
$$;
''')
    # fn_registrar_pago
    _exec(r'''
CREATE FUNCTION school.fn_registrar_pago(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying DEFAULT NULL::character varying, p_observaciones text DEFAULT NULL::text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_id_pago BIGINT;
BEGIN

    IF p_monto <= 0 THEN
        RAISE EXCEPTION
            'El monto del pago debe ser mayor a cero.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM estudiante
        WHERE id_estudiante = p_id_estudiante
    ) THEN
        RAISE EXCEPTION
            'El estudiante no existe.';
    END IF;

    INSERT INTO pago (
        id_estudiante,
        id_usuario,
        monto_total,
        metodo,
        referencia,
        observaciones,
        estado
    )
    VALUES (
        p_id_estudiante,
        p_id_usuario,
        p_monto,
        p_metodo,
        p_referencia,
        p_observaciones,
        'CONFIRMADO'
    )
    RETURNING id_pago INTO v_id_pago;

    RETURN v_id_pago;
END;
$$;
''')
    # fn_registrar_pago_automatico
    _exec(r'''
CREATE FUNCTION school.fn_registrar_pago_automatico(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying DEFAULT NULL::character varying, p_observaciones text DEFAULT NULL::text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_id_pago BIGINT;

    v_saldo NUMERIC(12,2);

    v_obligacion RECORD;

    v_saldo_obligacion NUMERIC(12,2);

    v_aplicar NUMERIC(12,2);
BEGIN

    -- Registrar pago

    v_id_pago :=
        fn_registrar_pago(
            p_id_estudiante,
            p_monto,
            p_metodo,
            p_referencia,
            p_observaciones,
            p_id_usuario
        );

    v_saldo := p_monto;

    -- Buscar obligaciones pendientes

    FOR v_obligacion IN

        SELECT
            o.id_obligacion,

            o.monto_neto
            -
            COALESCE(
                SUM(
                    CASE
                        WHEN p.estado = 'CONFIRMADO' THEN ap.monto_aplicado
                        ELSE 0
                    END
                ),
                0
            ) AS saldo

        FROM obligacion o

        JOIN inscripcion i
            ON i.id_inscripcion = o.id_inscripcion

        LEFT JOIN aplicacion_pago ap
            ON ap.id_obligacion = o.id_obligacion

        LEFT JOIN pago p
            ON p.id_pago = ap.id_pago
           AND p.estado = 'CONFIRMADO'

        WHERE i.id_estudiante = p_id_estudiante
          AND i.estado = 'ACTIVA'
          AND o.estado IN ('PENDIENTE', 'PARCIAL')

        GROUP BY
            o.id_obligacion,
            o.monto_neto,
            o.fecha_vencimiento

        HAVING
            o.monto_neto
            -
            COALESCE(
                SUM(
                    CASE
                        WHEN p.estado = 'CONFIRMADO' THEN ap.monto_aplicado
                        ELSE 0
                    END
                ),
                0
            ) > 0

        ORDER BY
            o.fecha_vencimiento NULLS LAST,
            o.id_obligacion

    LOOP

        EXIT WHEN v_saldo <= 0;

        v_saldo_obligacion := v_obligacion.saldo;

        v_aplicar :=
            LEAST(
                v_saldo,
                v_saldo_obligacion
            );

        PERFORM fn_aplicar_pago(
            v_id_pago,
            v_obligacion.id_obligacion,
            v_aplicar
        );

        v_saldo :=
            v_saldo - v_aplicar;

    END LOOP;

    -- Si sobra dinero crear saldo a favor

    IF v_saldo > 0 THEN

        INSERT INTO saldo_favor (
            id_estudiante,
            id_pago_origen,
            monto_original,
            monto_disponible,
            estado,
            observaciones
        )
        VALUES (
            p_id_estudiante,
            v_id_pago,
            v_saldo,
            v_saldo,
            'ACTIVO',
            'Saldo generado automáticamente'
        );

    END IF;

    RETURN v_id_pago;

END;
$$;
''')
    # fn_trasladar_saldo
    _exec(r'''
CREATE FUNCTION school.fn_trasladar_saldo(p_id_estudiante bigint, p_inscripcion_origen bigint, p_inscripcion_destino bigint, p_monto numeric, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_id_movimiento BIGINT;
BEGIN

    IF p_monto <= 0 THEN
        RAISE EXCEPTION
            'El monto debe ser mayor a cero.';
    END IF;

    INSERT INTO movimiento_saldo (
        id_estudiante,
        id_inscripcion_origen,
        id_inscripcion_destino,
        tipo,
        monto,
        motivo,
        estado,
        id_usuario
    )
    VALUES (
        p_id_estudiante,
        p_inscripcion_origen,
        p_inscripcion_destino,
        'TRASLADO_SALDO',
        p_monto,
        p_motivo,
        'APLICADO',
        p_id_usuario
    )
    RETURNING id_movimiento
    INTO v_id_movimiento;

    RETURN v_id_movimiento;
END;
$$;
''')
    # fn_trigger_actualizar_obligacion
    _exec(r'''
CREATE FUNCTION school.fn_trigger_actualizar_obligacion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
BEGIN

    IF TG_OP = 'UPDATE'
       AND OLD.id_obligacion IS DISTINCT FROM NEW.id_obligacion
    THEN
        PERFORM fn_actualizar_estado_obligacion(OLD.id_obligacion);
        PERFORM fn_actualizar_estado_obligacion(NEW.id_obligacion);
    ELSE
        PERFORM fn_actualizar_estado_obligacion(
            COALESCE(NEW.id_obligacion, OLD.id_obligacion)
        );
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;
''')
    # fn_validar_aplicacion_pago
    _exec(r'''
CREATE FUNCTION school.fn_validar_aplicacion_pago() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_monto_pago NUMERIC(12,2);
    v_total_aplicado_pago NUMERIC(12,2);

    v_monto_obligacion NUMERIC(12,2);
    v_total_aplicado_obligacion NUMERIC(12,2);

    v_estado_pago estado_pago;
    v_estado_obligacion estado_obligacion;
BEGIN

    SELECT monto_total, estado
    INTO v_monto_pago, v_estado_pago
    FROM pago
    WHERE id_pago = NEW.id_pago
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'El pago seleccionado no existe.';
    END IF;

    IF v_estado_pago <> 'CONFIRMADO' THEN
        RAISE EXCEPTION
            'No se pueden aplicar pagos que no estén confirmados.';
    END IF;

    SELECT COALESCE(SUM(monto_aplicado), 0)
    INTO v_total_aplicado_pago
    FROM aplicacion_pago
    WHERE id_pago = NEW.id_pago
      AND id_aplicacion <> COALESCE(NEW.id_aplicacion, 0);

    IF v_total_aplicado_pago + NEW.monto_aplicado > v_monto_pago THEN
        RAISE EXCEPTION
            'El monto aplicado excede el total del pago.';
    END IF;


    SELECT monto_neto, estado
    INTO v_monto_obligacion, v_estado_obligacion
    FROM obligacion
    WHERE id_obligacion = NEW.id_obligacion
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'La obligación seleccionada no existe.';
    END IF;

    IF v_estado_obligacion = 'ANULADA' THEN
        RAISE EXCEPTION
            'No se puede aplicar un pago a una obligación anulada.';
    END IF;

    SELECT COALESCE(SUM(ap.monto_aplicado), 0)
    INTO v_total_aplicado_obligacion
    FROM aplicacion_pago ap
    JOIN pago p
        ON p.id_pago = ap.id_pago
    WHERE ap.id_obligacion = NEW.id_obligacion
      AND p.estado = 'CONFIRMADO'
      AND ap.id_aplicacion <> COALESCE(NEW.id_aplicacion, 0);

    IF v_total_aplicado_obligacion + NEW.monto_aplicado > v_monto_obligacion THEN
        RAISE EXCEPTION
            'El monto aplicado excede el saldo de la obligación.';
    END IF;

    RETURN NEW;
END;
$$;
''')
    # fn_validar_descuentos_obligacion
    _exec(r'''
CREATE FUNCTION school.fn_validar_descuentos_obligacion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_total_descuentos NUMERIC(12,2);
    v_monto_bruto NUMERIC(12,2);
    v_monto_beca NUMERIC(12,2);
BEGIN

    SELECT
        monto_bruto,
        monto_beca
    INTO
        v_monto_bruto,
        v_monto_beca
    FROM obligacion
    WHERE id_obligacion = NEW.id_obligacion;

    SELECT COALESCE(
        SUM(monto_aplicado),
        0
    )
    INTO v_total_descuentos
    FROM descuento_obligacion
    WHERE id_obligacion = NEW.id_obligacion
      AND id_descuento_obligacion <>
          COALESCE(
              NEW.id_descuento_obligacion,
              0
          );

    IF
        v_total_descuentos
        + NEW.monto_aplicado
        + v_monto_beca
        > v_monto_bruto
    THEN

        RAISE EXCEPTION
            'Los descuentos y becas exceden el monto bruto de la obligación.';

    END IF;

    RETURN NEW;
END;
$$;
''')
    # fn_validar_grado_inscripcion
    _exec(r'''
CREATE FUNCTION school.fn_validar_grado_inscripcion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_carrera_ciclo_grado BIGINT;
BEGIN

    SELECT id_carrera_ciclo
    INTO v_carrera_ciclo_grado
    FROM grado
    WHERE id_grado = NEW.id_grado;

    IF v_carrera_ciclo_grado <> NEW.id_carrera_ciclo THEN

        RAISE EXCEPTION
            'El grado seleccionado no pertenece a la carrera/ciclo de la inscripción.';

    END IF;

    RETURN NEW;
END;
$$;
''')
    # fn_validar_movimiento_saldo
    _exec(r'''
CREATE FUNCTION school.fn_validar_movimiento_saldo() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_estudiante_origen BIGINT;
    v_estudiante_destino BIGINT;
BEGIN

    IF NEW.id_inscripcion_origen IS NOT NULL THEN

        SELECT id_estudiante
        INTO v_estudiante_origen
        FROM inscripcion
        WHERE id_inscripcion = NEW.id_inscripcion_origen;

        IF v_estudiante_origen <> NEW.id_estudiante THEN
            RAISE EXCEPTION
                'La inscripción origen no pertenece al estudiante.';
        END IF;

    END IF;

    IF NEW.id_inscripcion_destino IS NOT NULL THEN

        SELECT id_estudiante
        INTO v_estudiante_destino
        FROM inscripcion
        WHERE id_inscripcion = NEW.id_inscripcion_destino;

        IF v_estudiante_destino <> NEW.id_estudiante THEN
            RAISE EXCEPTION
                'La inscripción destino no pertenece al estudiante.';
        END IF;

    END IF;

    RETURN NEW;
END;
$$;
''')
    # fn_validar_propietario_pago_obligacion
    _exec(r'''
CREATE FUNCTION school.fn_validar_propietario_pago_obligacion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path = school, pg_catalog
    AS $$
DECLARE
    v_estudiante_pago BIGINT;
    v_estudiante_obligacion BIGINT;
BEGIN

    SELECT id_estudiante
    INTO v_estudiante_pago
    FROM pago
    WHERE id_pago = NEW.id_pago;

    SELECT i.id_estudiante
    INTO v_estudiante_obligacion
    FROM obligacion o
    JOIN inscripcion i
        ON i.id_inscripcion = o.id_inscripcion
    WHERE o.id_obligacion = NEW.id_obligacion;

    IF v_estudiante_pago IS NULL THEN
        RAISE EXCEPTION
            'El pago seleccionado no existe.';
    END IF;

    IF v_estudiante_obligacion IS NULL THEN
        RAISE EXCEPTION
            'La obligación seleccionada no existe.';
    END IF;

    IF v_estudiante_pago <> v_estudiante_obligacion THEN
        RAISE EXCEPTION
            'No se puede aplicar un pago a una obligación de otro estudiante.';
    END IF;

    RETURN NEW;
END;
$$;
''')
    # Vistas dependientes de vw_saldo_obligaciones.
    # vw_estudiantes_insolventes
    _exec(r'''
CREATE OR REPLACE VIEW school.vw_estudiantes_insolventes AS
 SELECT e.id_estudiante,
    e.codigo_estudiante,
    concat(e.nombres, ' ', e.apellidos) AS estudiante,
    i.id_inscripcion,
    g.nombre AS grado,
    COALESCE(sum(v.saldo), (0)::numeric) AS deuda_total
   FROM (((school.estudiante e
     JOIN school.inscripcion i ON ((i.id_estudiante = e.id_estudiante)))
     JOIN school.grado g ON ((g.id_grado = i.id_grado)))
     JOIN school.vw_saldo_obligaciones v ON ((v.id_inscripcion = i.id_inscripcion)))
  WHERE (i.estado = 'ACTIVA'::school.estado_inscripcion)
  GROUP BY e.id_estudiante, e.codigo_estudiante, e.nombres, e.apellidos, i.id_inscripcion, g.nombre
 HAVING (COALESCE(sum(v.saldo), (0)::numeric) > (0)::numeric);
''')
    # vw_dashboard_financiero
    _exec(r'''
CREATE OR REPLACE VIEW school.vw_dashboard_financiero AS
 SELECT ( SELECT count(*) AS count
           FROM school.estudiante
          WHERE (estudiante.estado = 'ACTIVO'::school.estado_estudiante)) AS estudiantes_activos,
    ( SELECT count(*) AS count
           FROM school.inscripcion
          WHERE (inscripcion.estado = 'ACTIVA'::school.estado_inscripcion)) AS inscripciones_activas,
    ( SELECT COALESCE(sum(pago.monto_total), (0)::numeric) AS "coalesce"
           FROM school.pago
          WHERE (pago.estado = 'CONFIRMADO'::school.estado_pago)) AS total_pagado,
    ( SELECT COALESCE(sum(vw_saldo_obligaciones.saldo), (0)::numeric) AS "coalesce"
           FROM school.vw_saldo_obligaciones) AS deuda_total,
    ( SELECT count(*) AS count
           FROM school.vw_estudiantes_insolventes) AS estudiantes_insolventes;
''')
    # vw_deuda_por_estudiante
    _exec(r'''
CREATE OR REPLACE VIEW school.vw_deuda_por_estudiante AS
 SELECT e.id_estudiante,
    e.codigo_estudiante,
    concat(e.nombres, ' ', e.apellidos) AS estudiante,
    g.nombre AS grado,
    COALESCE(sum(v.saldo), (0)::numeric) AS deuda_total
   FROM (((school.estudiante e
     JOIN school.inscripcion i ON ((i.id_estudiante = e.id_estudiante)))
     JOIN school.grado g ON ((g.id_grado = i.id_grado)))
     JOIN school.vw_saldo_obligaciones v ON ((v.id_inscripcion = i.id_inscripcion)))
  WHERE (i.estado = 'ACTIVA'::school.estado_inscripcion)
  GROUP BY e.id_estudiante, e.codigo_estudiante, e.nombres, e.apellidos, g.nombre;
''')
    # vw_deuda_por_grado
    _exec(r'''
CREATE OR REPLACE VIEW school.vw_deuda_por_grado AS
 SELECT g.id_grado,
    g.nombre AS grado,
    count(DISTINCT i.id_estudiante) AS cantidad_estudiantes,
    COALESCE(sum(v.saldo), (0)::numeric) AS deuda_total
   FROM ((school.grado g
     JOIN school.inscripcion i ON ((i.id_grado = g.id_grado)))
     JOIN school.vw_saldo_obligaciones v ON ((v.id_inscripcion = i.id_inscripcion)))
  WHERE (i.estado = 'ACTIVA'::school.estado_inscripcion)
  GROUP BY g.id_grado, g.nombre;
''')
    # vw_estado_cuenta_estudiante
    _exec(r'''
CREATE OR REPLACE VIEW school.vw_estado_cuenta_estudiante AS
 SELECT e.id_estudiante,
    e.codigo_estudiante,
    concat(e.nombres, ' ', e.apellidos) AS estudiante,
    i.id_inscripcion,
    c.nombre AS carrera,
    g.nombre AS grado,
    o.id_obligacion,
    o.concepto,
    o.periodo,
    o.fecha_vencimiento,
    s.total_pagado,
    s.saldo
   FROM ((((((school.estudiante e
     JOIN school.inscripcion i ON ((i.id_estudiante = e.id_estudiante)))
     JOIN school.carrera_ciclo cc ON ((cc.id_carrera_ciclo = i.id_carrera_ciclo)))
     JOIN school.carrera c ON ((c.id_carrera = cc.id_carrera)))
     JOIN school.grado g ON ((g.id_grado = i.id_grado)))
     JOIN school.obligacion o ON ((o.id_inscripcion = i.id_inscripcion)))
     JOIN school.vw_saldo_obligaciones s ON ((s.id_obligacion = o.id_obligacion)));
''')
    # Triggers.
    # trg_actualizar_estado_obligacion
    _exec(r'''
CREATE TRIGGER trg_actualizar_estado_obligacion AFTER INSERT OR DELETE OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_trigger_actualizar_obligacion();
''')
    # trg_recalcular_obligaciones_pago_anulado
    _exec(r'''
CREATE TRIGGER trg_recalcular_obligaciones_pago_anulado AFTER UPDATE ON school.pago FOR EACH ROW EXECUTE FUNCTION school.fn_recalcular_obligaciones_pago_anulado();
''')
    # trg_validar_aplicacion_pago
    _exec(r'''
CREATE TRIGGER trg_validar_aplicacion_pago BEFORE INSERT OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_validar_aplicacion_pago();
''')
    # trg_validar_descuentos_obligacion
    _exec(r'''
CREATE TRIGGER trg_validar_descuentos_obligacion BEFORE INSERT OR UPDATE ON school.descuento_obligacion FOR EACH ROW EXECUTE FUNCTION school.fn_validar_descuentos_obligacion();
''')
    # trg_validar_grado_inscripcion
    _exec(r'''
CREATE TRIGGER trg_validar_grado_inscripcion BEFORE INSERT OR UPDATE ON school.inscripcion FOR EACH ROW EXECUTE FUNCTION school.fn_validar_grado_inscripcion();
''')
    # trg_validar_movimiento_saldo
    _exec(r'''
CREATE TRIGGER trg_validar_movimiento_saldo BEFORE INSERT OR UPDATE ON school.movimiento_saldo FOR EACH ROW EXECUTE FUNCTION school.fn_validar_movimiento_saldo();
''')
    # trg_validar_propietario_pago_obligacion
    _exec(r'''
CREATE TRIGGER trg_validar_propietario_pago_obligacion BEFORE INSERT OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_validar_propietario_pago_obligacion();
''')


def downgrade() -> None:
    # Primero se eliminan los triggers que dependen de las funciones.
    _exec("DROP TRIGGER IF EXISTS trg_validar_propietario_pago_obligacion ON school.aplicacion_pago")
    _exec("DROP TRIGGER IF EXISTS trg_validar_movimiento_saldo ON school.movimiento_saldo")
    _exec("DROP TRIGGER IF EXISTS trg_validar_grado_inscripcion ON school.inscripcion")
    _exec("DROP TRIGGER IF EXISTS trg_validar_descuentos_obligacion ON school.descuento_obligacion")
    _exec("DROP TRIGGER IF EXISTS trg_validar_aplicacion_pago ON school.aplicacion_pago")
    _exec("DROP TRIGGER IF EXISTS trg_recalcular_obligaciones_pago_anulado ON school.pago")
    _exec("DROP TRIGGER IF EXISTS trg_actualizar_estado_obligacion ON school.aplicacion_pago")

    # Luego las vistas dependientes.
    _exec("DROP VIEW IF EXISTS school.vw_dashboard_financiero")
    _exec("DROP VIEW IF EXISTS school.vw_deuda_por_estudiante")
    _exec("DROP VIEW IF EXISTS school.vw_deuda_por_grado")
    _exec("DROP VIEW IF EXISTS school.vw_estado_cuenta_estudiante")
    _exec("DROP VIEW IF EXISTS school.vw_estudiantes_insolventes")

    # Las funciones se eliminan con su firma exacta para evitar ambigüedad.
    _exec("DROP FUNCTION IF EXISTS school.fn_validar_propietario_pago_obligacion()")
    _exec("DROP FUNCTION IF EXISTS school.fn_validar_movimiento_saldo()")
    _exec("DROP FUNCTION IF EXISTS school.fn_validar_grado_inscripcion()")
    _exec("DROP FUNCTION IF EXISTS school.fn_validar_descuentos_obligacion()")
    _exec("DROP FUNCTION IF EXISTS school.fn_validar_aplicacion_pago()")
    _exec("DROP FUNCTION IF EXISTS school.fn_trigger_actualizar_obligacion()")
    _exec("DROP FUNCTION IF EXISTS school.fn_trasladar_saldo(bigint, bigint, bigint, numeric, text, bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_registrar_pago_automatico(bigint, numeric, school.metodo_pago, character varying, text, bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_registrar_pago(bigint, numeric, school.metodo_pago, character varying, text, bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_registrar_auditoria(bigint, character varying, character varying, character varying, bigint, text, jsonb, jsonb)")
    _exec("DROP FUNCTION IF EXISTS school.fn_recalcular_obligaciones_pago_anulado()")
    _exec("DROP FUNCTION IF EXISTS school.fn_generar_solvencia(bigint, bigint, bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_generar_recibo(bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_generar_obligaciones_mensuales(bigint, bigint, date, integer)")
    _exec("DROP FUNCTION IF EXISTS school.fn_cambiar_carrera(bigint, bigint, bigint, bigint, text, bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_calcular_saldo_corte(bigint, date)")
    _exec("DROP FUNCTION IF EXISTS school.fn_aplicar_saldo_favor(bigint, bigint, numeric)")
    _exec("DROP FUNCTION IF EXISTS school.fn_aplicar_pago(bigint, bigint, numeric)")
    _exec("DROP FUNCTION IF EXISTS school.fn_saldo_disponible_pago(bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_aplicar_descuento_obligacion(bigint, bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_aplicar_beca_obligacion(bigint, numeric)")
    _exec("DROP FUNCTION IF EXISTS school.fn_anular_pago(bigint, text, bigint)")
    _exec("DROP FUNCTION IF EXISTS school.fn_actualizar_estado_obligacion(bigint)")

    # La vista base se elimina al final porque fn_calcular_saldo_corte depende de ella.
    _exec("DROP VIEW IF EXISTS school.vw_saldo_obligaciones")
