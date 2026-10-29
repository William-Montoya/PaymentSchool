--
-- PostgreSQL database dump
--

\restrict lfKILKxCngeHCCqEUhrsTPDKY0SaNMGeYYdkPVcCvDomQO13xl8mogc9DJYbhWM

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: school; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA school;


--
-- Name: estado_beca; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_beca AS ENUM (
    'PENDIENTE',
    'ACTIVA',
    'FINALIZADA',
    'CANCELADA'
);


--
-- Name: estado_cambio_carrera; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_cambio_carrera AS ENUM (
    'SOLICITADO',
    'APROBADO',
    'RECHAZADO',
    'CANCELADO'
);


--
-- Name: estado_ciclo; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_ciclo AS ENUM (
    'PLANIFICADO',
    'ACTIVO',
    'CERRADO'
);


--
-- Name: estado_estudiante; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_estudiante AS ENUM (
    'ACTIVO',
    'INACTIVO',
    'RETIRADO',
    'EGRESADO'
);


--
-- Name: estado_inscripcion; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_inscripcion AS ENUM (
    'ACTIVA',
    'FINALIZADA',
    'CANCELADA',
    'RETIRADA'
);


--
-- Name: estado_movimiento_saldo; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_movimiento_saldo AS ENUM (
    'PENDIENTE',
    'APLICADO',
    'ANULADO'
);


--
-- Name: estado_obligacion; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_obligacion AS ENUM (
    'PENDIENTE',
    'PARCIAL',
    'PAGADA',
    'ANULADA'
);


--
-- Name: estado_pago; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_pago AS ENUM (
    'PENDIENTE',
    'CONFIRMADO',
    'ANULADO'
);


--
-- Name: estado_solvencia; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_solvencia AS ENUM (
    'SOLVENTE',
    'INSOLVENTE'
);


--
-- Name: estado_usuario; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.estado_usuario AS ENUM (
    'ACTIVO',
    'INACTIVO',
    'BLOQUEADO'
);


--
-- Name: metodo_pago; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.metodo_pago AS ENUM (
    'EFECTIVO',
    'TRANSFERENCIA',
    'DEPOSITO',
    'TARJETA',
    'OTRO'
);


--
-- Name: tipo_inscripcion; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.tipo_inscripcion AS ENUM (
    'NUEVA',
    'REINSCRIPCION',
    'TRASLADO'
);


--
-- Name: tipo_movimiento_saldo; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.tipo_movimiento_saldo AS ENUM (
    'TRASLADO_SALDO',
    'AJUSTE',
    'DEVOLUCION',
    'COMPENSACION'
);


--
-- Name: tipo_precio; Type: TYPE; Schema: school; Owner: -
--

CREATE TYPE school.tipo_precio AS ENUM (
    'INSCRIPCION',
    'MENSUALIDAD',
    'OTRO'
);


--
-- Name: fn_actualizar_estado_obligacion(bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_actualizar_estado_obligacion(p_id_obligacion bigint) RETURNS void
    LANGUAGE plpgsql
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
    WHERE id_obligacion = p_id_obligacion;

END;
$$;


--
-- Name: fn_anular_pago(bigint, text, bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_anular_pago(p_id_pago bigint, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS void
    LANGUAGE plpgsql
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


--
-- Name: fn_aplicar_beca_obligacion(bigint, numeric); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_aplicar_beca_obligacion(p_id_obligacion bigint, p_porcentaje numeric) RETURNS void
    LANGUAGE plpgsql
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


--
-- Name: fn_aplicar_descuento_obligacion(bigint, bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_aplicar_descuento_obligacion(p_id_obligacion bigint, p_id_descuento bigint) RETURNS void
    LANGUAGE plpgsql
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


--
-- Name: fn_aplicar_pago(bigint, bigint, numeric); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_aplicar_pago(p_id_pago bigint, p_id_obligacion bigint, p_monto numeric) RETURNS bigint
    LANGUAGE plpgsql
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


--
-- Name: fn_aplicar_saldo_favor(bigint, bigint, numeric); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_aplicar_saldo_favor(p_id_saldo_favor bigint, p_id_obligacion bigint, p_monto numeric) RETURNS void
    LANGUAGE plpgsql
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


--
-- Name: fn_calcular_saldo_corte(bigint, date); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_calcular_saldo_corte(p_id_inscripcion bigint, p_fecha_corte date) RETURNS numeric
    LANGUAGE sql
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


--
-- Name: fn_cambiar_carrera(bigint, bigint, bigint, bigint, text, bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_cambiar_carrera(p_id_estudiante bigint, p_id_inscripcion_origen bigint, p_id_carrera_ciclo_destino bigint, p_id_grado_destino bigint, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
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


--
-- Name: fn_generar_obligaciones_mensuales(bigint, bigint, date, integer); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_generar_obligaciones_mensuales(p_id_inscripcion bigint, p_id_precio bigint, p_fecha_inicio date, p_cantidad_meses integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_monto NUMERIC(12,2);

    v_fecha DATE;

    v_contador INTEGER;

    v_periodo VARCHAR(20);
BEGIN

    SELECT monto
    INTO v_monto
    FROM precio_carrera
    WHERE id_precio = p_id_precio
      AND tipo = 'MENSUALIDAD'
      AND activo = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No existe un precio de mensualidad activo.';
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
            estado
        )
        VALUES (
            p_id_inscripcion,
            p_id_precio,
            'Mensualidad',
            v_periodo,
            v_fecha,
            v_monto,
            v_monto,
            'PENDIENTE'
        );

    END LOOP;

END;
$$;


--
-- Name: fn_generar_recibo(bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_generar_recibo(p_id_pago bigint) RETURNS bigint
    LANGUAGE plpgsql
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


--
-- Name: fn_generar_solvencia(bigint, bigint, bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_generar_solvencia(p_id_estudiante bigint, p_id_inscripcion bigint, p_id_evaluacion bigint) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_fecha_corte DATE;
    v_saldo NUMERIC(12,2);
    v_estado estado_solvencia;
    v_codigo VARCHAR(100);
    v_id BIGINT;
BEGIN

    SELECT fecha_corte_finanzas
    INTO v_fecha_corte
    FROM evaluacion
    WHERE id_evaluacion = p_id_evaluacion;

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


--
-- Name: fn_recalcular_obligaciones_pago_anulado(); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_recalcular_obligaciones_pago_anulado() RETURNS trigger
    LANGUAGE plpgsql
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


--
-- Name: fn_registrar_auditoria(bigint, character varying, character varying, character varying, bigint, text, jsonb, jsonb); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_registrar_auditoria(p_id_usuario bigint, p_modulo character varying, p_accion character varying, p_tabla character varying, p_id_registro bigint, p_descripcion text, p_datos_anteriores jsonb DEFAULT NULL::jsonb, p_datos_nuevos jsonb DEFAULT NULL::jsonb) RETURNS void
    LANGUAGE plpgsql
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


--
-- Name: fn_registrar_pago(bigint, numeric, school.metodo_pago, character varying, text, bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_registrar_pago(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying DEFAULT NULL::character varying, p_observaciones text DEFAULT NULL::text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
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


--
-- Name: fn_registrar_pago_automatico(bigint, numeric, school.metodo_pago, character varying, text, bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_registrar_pago_automatico(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying DEFAULT NULL::character varying, p_observaciones text DEFAULT NULL::text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
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
                SUM(ap.monto_aplicado),
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
                SUM(ap.monto_aplicado),
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


--
-- Name: fn_saldo_disponible_pago(bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_saldo_disponible_pago(p_id_pago bigint) RETURNS numeric
    LANGUAGE sql
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


--
-- Name: fn_trasladar_saldo(bigint, bigint, bigint, numeric, text, bigint); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_trasladar_saldo(p_id_estudiante bigint, p_inscripcion_origen bigint, p_inscripcion_destino bigint, p_monto numeric, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
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


--
-- Name: fn_trigger_actualizar_obligacion(); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_trigger_actualizar_obligacion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

    PERFORM fn_actualizar_estado_obligacion(
        COALESCE(NEW.id_obligacion, OLD.id_obligacion)
    );

    RETURN COALESCE(NEW, OLD);
END;
$$;


--
-- Name: fn_validar_aplicacion_pago(); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_validar_aplicacion_pago() RETURNS trigger
    LANGUAGE plpgsql
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
    WHERE id_pago = NEW.id_pago;

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
    WHERE id_obligacion = NEW.id_obligacion;

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


--
-- Name: fn_validar_descuentos_obligacion(); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_validar_descuentos_obligacion() RETURNS trigger
    LANGUAGE plpgsql
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


--
-- Name: fn_validar_grado_inscripcion(); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_validar_grado_inscripcion() RETURNS trigger
    LANGUAGE plpgsql
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


--
-- Name: fn_validar_movimiento_saldo(); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_validar_movimiento_saldo() RETURNS trigger
    LANGUAGE plpgsql
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


--
-- Name: fn_validar_propietario_pago_obligacion(); Type: FUNCTION; Schema: school; Owner: -
--

CREATE FUNCTION school.fn_validar_propietario_pago_obligacion() RETURNS trigger
    LANGUAGE plpgsql
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


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: aplicacion_pago; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.aplicacion_pago (
    id_aplicacion bigint NOT NULL,
    id_pago bigint NOT NULL,
    id_obligacion bigint NOT NULL,
    monto_aplicado numeric(12,2) NOT NULL,
    fecha_aplicacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_aplicacion_monto CHECK ((monto_aplicado > (0)::numeric))
);


--
-- Name: aplicacion_pago_id_aplicacion_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.aplicacion_pago_id_aplicacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: aplicacion_pago_id_aplicacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.aplicacion_pago_id_aplicacion_seq OWNED BY school.aplicacion_pago.id_aplicacion;


--
-- Name: auditoria; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.auditoria (
    id_auditoria bigint NOT NULL,
    id_usuario bigint,
    fecha_evento timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modulo character varying(100),
    accion character varying(100),
    tabla_afectada character varying(100),
    id_registro bigint,
    descripcion text,
    datos_anteriores jsonb,
    datos_nuevos jsonb,
    ip character varying(45)
);


--
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.auditoria_id_auditoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.auditoria_id_auditoria_seq OWNED BY school.auditoria.id_auditoria;


--
-- Name: beca; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.beca (
    id_beca bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    porcentaje numeric(5,2) NOT NULL,
    convenio character varying(200),
    estado school.estado_beca DEFAULT 'ACTIVA'::school.estado_beca NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    CONSTRAINT ck_beca_fechas CHECK (((fecha_fin IS NULL) OR (fecha_inicio IS NULL) OR (fecha_fin >= fecha_inicio))),
    CONSTRAINT ck_beca_porcentaje CHECK (((porcentaje >= (0)::numeric) AND (porcentaje <= (100)::numeric)))
);


--
-- Name: beca_estudiante; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.beca_estudiante (
    id_beca_estudiante bigint NOT NULL,
    id_beca bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date,
    porcentaje_aplicado numeric(5,2),
    observaciones text,
    CONSTRAINT ck_beca_estudiante_porcentaje CHECK (((porcentaje_aplicado IS NULL) OR ((porcentaje_aplicado >= (0)::numeric) AND (porcentaje_aplicado <= (100)::numeric))))
);


--
-- Name: beca_estudiante_id_beca_estudiante_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.beca_estudiante_id_beca_estudiante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: beca_estudiante_id_beca_estudiante_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.beca_estudiante_id_beca_estudiante_seq OWNED BY school.beca_estudiante.id_beca_estudiante;


--
-- Name: beca_id_beca_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.beca_id_beca_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: beca_id_beca_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.beca_id_beca_seq OWNED BY school.beca.id_beca;


--
-- Name: cambio_carrera; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.cambio_carrera (
    id_cambio bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    id_inscripcion_origen bigint NOT NULL,
    id_inscripcion_destino bigint,
    fecha_solicitud timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_aprobacion timestamp without time zone,
    motivo text,
    estado school.estado_cambio_carrera DEFAULT 'SOLICITADO'::school.estado_cambio_carrera NOT NULL,
    id_usuario bigint,
    observaciones text
);


--
-- Name: cambio_carrera_id_cambio_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.cambio_carrera_id_cambio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cambio_carrera_id_cambio_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.cambio_carrera_id_cambio_seq OWNED BY school.cambio_carrera.id_cambio;


--
-- Name: carrera; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.carrera (
    id_carrera bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: carrera_ciclo; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.carrera_ciclo (
    id_carrera_ciclo bigint NOT NULL,
    id_carrera bigint NOT NULL,
    id_ciclo bigint NOT NULL,
    nombre_comercial character varying(150),
    estado boolean DEFAULT true NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: carrera_ciclo_id_carrera_ciclo_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.carrera_ciclo_id_carrera_ciclo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: carrera_ciclo_id_carrera_ciclo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.carrera_ciclo_id_carrera_ciclo_seq OWNED BY school.carrera_ciclo.id_carrera_ciclo;


--
-- Name: carrera_id_carrera_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.carrera_id_carrera_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: carrera_id_carrera_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.carrera_id_carrera_seq OWNED BY school.carrera.id_carrera;


--
-- Name: ciclo_escolar; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.ciclo_escolar (
    id_ciclo bigint NOT NULL,
    nombre character varying(100) NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    estado school.estado_ciclo DEFAULT 'PLANIFICADO'::school.estado_ciclo NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_ciclo_fechas CHECK ((fecha_fin >= fecha_inicio))
);


--
-- Name: ciclo_escolar_id_ciclo_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.ciclo_escolar_id_ciclo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ciclo_escolar_id_ciclo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.ciclo_escolar_id_ciclo_seq OWNED BY school.ciclo_escolar.id_ciclo;


--
-- Name: contacto; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.contacto (
    id_contacto bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    parentesco character varying(100),
    telefono character varying(30),
    whatsapp character varying(30),
    email character varying(150),
    es_principal boolean DEFAULT false NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: contacto_id_contacto_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.contacto_id_contacto_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: contacto_id_contacto_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.contacto_id_contacto_seq OWNED BY school.contacto.id_contacto;


--
-- Name: descuento; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.descuento (
    id_descuento bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    porcentaje numeric(5,2),
    monto_fijo numeric(12,2),
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_descuento_monto CHECK (((monto_fijo IS NULL) OR (monto_fijo >= (0)::numeric))),
    CONSTRAINT ck_descuento_porcentaje CHECK (((porcentaje IS NULL) OR ((porcentaje >= (0)::numeric) AND (porcentaje <= (100)::numeric)))),
    CONSTRAINT ck_descuento_tipo CHECK (((porcentaje IS NOT NULL) OR (monto_fijo IS NOT NULL)))
);


--
-- Name: descuento_id_descuento_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.descuento_id_descuento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: descuento_id_descuento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.descuento_id_descuento_seq OWNED BY school.descuento.id_descuento;


--
-- Name: descuento_obligacion; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.descuento_obligacion (
    id_descuento_obligacion bigint NOT NULL,
    id_descuento bigint NOT NULL,
    id_obligacion bigint NOT NULL,
    monto_aplicado numeric(12,2) NOT NULL,
    fecha_aplicacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_descuento_aplicado CHECK ((monto_aplicado > (0)::numeric))
);


--
-- Name: descuento_obligacion_id_descuento_obligacion_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.descuento_obligacion_id_descuento_obligacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: descuento_obligacion_id_descuento_obligacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.descuento_obligacion_id_descuento_obligacion_seq OWNED BY school.descuento_obligacion.id_descuento_obligacion;


--
-- Name: documento_expediente; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.documento_expediente (
    id_documento bigint NOT NULL,
    id_expediente bigint NOT NULL,
    id_tipo_documento bigint NOT NULL,
    nombre_archivo character varying(255),
    ruta_archivo text,
    fecha_entrega date,
    entregado boolean DEFAULT false NOT NULL,
    observaciones text,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: documento_expediente_id_documento_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.documento_expediente_id_documento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: documento_expediente_id_documento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.documento_expediente_id_documento_seq OWNED BY school.documento_expediente.id_documento;


--
-- Name: empleado; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.empleado (
    id_empleado bigint NOT NULL,
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    telefono character varying(30),
    email character varying(150),
    cargo character varying(100),
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: empleado_id_empleado_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.empleado_id_empleado_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empleado_id_empleado_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.empleado_id_empleado_seq OWNED BY school.empleado.id_empleado;


--
-- Name: estudiante; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.estudiante (
    id_estudiante bigint NOT NULL,
    codigo_estudiante character varying(50) NOT NULL,
    cui character varying(30),
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    fecha_nacimiento date,
    telefono character varying(30),
    whatsapp character varying(30),
    email character varying(150),
    direccion text,
    estado school.estado_estudiante DEFAULT 'ACTIVO'::school.estado_estudiante NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: estudiante_id_estudiante_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.estudiante_id_estudiante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estudiante_id_estudiante_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.estudiante_id_estudiante_seq OWNED BY school.estudiante.id_estudiante;


--
-- Name: evaluacion; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.evaluacion (
    id_evaluacion bigint NOT NULL,
    id_ciclo bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    fecha_evaluacion date NOT NULL,
    fecha_corte_finanzas date NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: evaluacion_id_evaluacion_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.evaluacion_id_evaluacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: evaluacion_id_evaluacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.evaluacion_id_evaluacion_seq OWNED BY school.evaluacion.id_evaluacion;


--
-- Name: expediente; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.expediente (
    id_expediente bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    observaciones text,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: expediente_id_expediente_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.expediente_id_expediente_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: expediente_id_expediente_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.expediente_id_expediente_seq OWNED BY school.expediente.id_expediente;


--
-- Name: grado; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.grado (
    id_grado bigint NOT NULL,
    id_carrera_ciclo bigint NOT NULL,
    nombre character varying(100) NOT NULL,
    nivel_orden integer,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_grado_orden CHECK (((nivel_orden IS NULL) OR (nivel_orden > 0)))
);


--
-- Name: grado_id_grado_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.grado_id_grado_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: grado_id_grado_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.grado_id_grado_seq OWNED BY school.grado.id_grado;


--
-- Name: inscripcion; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.inscripcion (
    id_inscripcion bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    id_carrera_ciclo bigint NOT NULL,
    id_grado bigint NOT NULL,
    fecha_inscripcion date DEFAULT CURRENT_DATE NOT NULL,
    tipo school.tipo_inscripcion DEFAULT 'NUEVA'::school.tipo_inscripcion NOT NULL,
    estado school.estado_inscripcion DEFAULT 'ACTIVA'::school.estado_inscripcion NOT NULL,
    observaciones text,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: inscripcion_id_inscripcion_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.inscripcion_id_inscripcion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inscripcion_id_inscripcion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.inscripcion_id_inscripcion_seq OWNED BY school.inscripcion.id_inscripcion;


--
-- Name: movimiento_saldo; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.movimiento_saldo (
    id_movimiento bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    id_inscripcion_origen bigint,
    id_inscripcion_destino bigint,
    tipo school.tipo_movimiento_saldo NOT NULL,
    monto numeric(12,2) NOT NULL,
    fecha_movimiento timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    motivo text,
    estado school.estado_movimiento_saldo DEFAULT 'PENDIENTE'::school.estado_movimiento_saldo NOT NULL,
    id_usuario bigint,
    referencia character varying(100),
    CONSTRAINT ck_movimiento_monto CHECK ((monto > (0)::numeric))
);


--
-- Name: movimiento_saldo_id_movimiento_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.movimiento_saldo_id_movimiento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: movimiento_saldo_id_movimiento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.movimiento_saldo_id_movimiento_seq OWNED BY school.movimiento_saldo.id_movimiento;


--
-- Name: notificacion; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.notificacion (
    id_notificacion bigint NOT NULL,
    titulo character varying(200) NOT NULL,
    mensaje text NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_usuario bigint,
    CONSTRAINT ck_notificacion_mensaje CHECK ((length(TRIM(BOTH FROM mensaje)) > 0))
);


--
-- Name: notificacion_destinatario; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.notificacion_destinatario (
    id_destinatario bigint NOT NULL,
    id_notificacion bigint NOT NULL,
    id_contacto bigint NOT NULL,
    estado character varying(30) DEFAULT 'GENERADO'::character varying NOT NULL,
    fecha_generado timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_abierto timestamp without time zone
);


--
-- Name: notificacion_destinatario_id_destinatario_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.notificacion_destinatario_id_destinatario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notificacion_destinatario_id_destinatario_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.notificacion_destinatario_id_destinatario_seq OWNED BY school.notificacion_destinatario.id_destinatario;


--
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.notificacion_id_notificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.notificacion_id_notificacion_seq OWNED BY school.notificacion.id_notificacion;


--
-- Name: obligacion; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.obligacion (
    id_obligacion bigint NOT NULL,
    id_inscripcion bigint NOT NULL,
    id_precio bigint,
    concepto character varying(150) NOT NULL,
    periodo character varying(20),
    fecha_vencimiento date,
    monto_bruto numeric(12,2) NOT NULL,
    monto_descuento numeric(12,2) DEFAULT 0 NOT NULL,
    monto_beca numeric(12,2) DEFAULT 0 NOT NULL,
    monto_neto numeric(12,2) NOT NULL,
    estado school.estado_obligacion DEFAULT 'PENDIENTE'::school.estado_obligacion NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tipo_obligacion character varying(30) NOT NULL,
    CONSTRAINT ck_obligacion_beca CHECK ((monto_beca >= (0)::numeric)),
    CONSTRAINT ck_obligacion_bruto CHECK ((monto_bruto >= (0)::numeric)),
    CONSTRAINT ck_obligacion_descuento CHECK ((monto_descuento >= (0)::numeric)),
    CONSTRAINT ck_obligacion_descuentos CHECK (((monto_descuento + monto_beca) <= monto_bruto)),
    CONSTRAINT ck_obligacion_neto CHECK ((monto_neto >= (0)::numeric)),
    CONSTRAINT ck_obligacion_tipo CHECK (((tipo_obligacion)::text = ANY ((ARRAY['INSCRIPCION'::character varying, 'MENSUALIDAD'::character varying, 'CERTIFICACION'::character varying, 'CONSTANCIA'::character varying, 'OTRO'::character varying])::text[])))
);


--
-- Name: obligacion_id_obligacion_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.obligacion_id_obligacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: obligacion_id_obligacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.obligacion_id_obligacion_seq OWNED BY school.obligacion.id_obligacion;


--
-- Name: pago; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.pago (
    id_pago bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    id_usuario bigint,
    fecha_pago timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    monto_total numeric(12,2) NOT NULL,
    metodo school.metodo_pago NOT NULL,
    referencia character varying(150),
    observaciones text,
    estado school.estado_pago DEFAULT 'CONFIRMADO'::school.estado_pago NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_pago_monto CHECK ((monto_total > (0)::numeric))
);


--
-- Name: pago_id_pago_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.pago_id_pago_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pago_id_pago_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.pago_id_pago_seq OWNED BY school.pago.id_pago;


--
-- Name: permiso; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.permiso (
    id_permiso bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text
);


--
-- Name: permiso_id_permiso_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.permiso_id_permiso_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permiso_id_permiso_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.permiso_id_permiso_seq OWNED BY school.permiso.id_permiso;


--
-- Name: precio_carrera; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.precio_carrera (
    id_precio bigint NOT NULL,
    id_carrera_ciclo bigint NOT NULL,
    tipo school.tipo_precio NOT NULL,
    concepto character varying(150) NOT NULL,
    monto numeric(12,2) NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_precio_fechas CHECK (((fecha_fin IS NULL) OR (fecha_fin >= fecha_inicio))),
    CONSTRAINT ck_precio_monto CHECK ((monto >= (0)::numeric))
);


--
-- Name: precio_carrera_id_precio_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.precio_carrera_id_precio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: precio_carrera_id_precio_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.precio_carrera_id_precio_seq OWNED BY school.precio_carrera.id_precio;


--
-- Name: recibo; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.recibo (
    id_recibo bigint NOT NULL,
    id_pago bigint NOT NULL,
    numero_recibo character varying(50) NOT NULL,
    codigo_verificacion character varying(100) NOT NULL,
    fecha_emision timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: recibo_id_recibo_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.recibo_id_recibo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: recibo_id_recibo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.recibo_id_recibo_seq OWNED BY school.recibo.id_recibo;


--
-- Name: rol; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.rol (
    id_rol bigint NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: rol_id_rol_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.rol_id_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rol_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.rol_id_rol_seq OWNED BY school.rol.id_rol;


--
-- Name: rol_permiso; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.rol_permiso (
    id_rol bigint NOT NULL,
    id_permiso bigint NOT NULL
);


--
-- Name: saldo_favor; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.saldo_favor (
    id_saldo_favor bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    id_pago_origen bigint,
    monto_original numeric(12,2) NOT NULL,
    monto_disponible numeric(12,2) NOT NULL,
    fecha_generacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado character varying(20) DEFAULT 'ACTIVO'::character varying NOT NULL,
    observaciones text,
    CONSTRAINT ck_saldo_favor_disponible CHECK (((monto_disponible >= (0)::numeric) AND (monto_disponible <= monto_original))),
    CONSTRAINT ck_saldo_favor_estado CHECK (((estado)::text = ANY ((ARRAY['ACTIVO'::character varying, 'AGOTADO'::character varying, 'ANULADO'::character varying])::text[]))),
    CONSTRAINT ck_saldo_favor_original CHECK ((monto_original > (0)::numeric))
);


--
-- Name: saldo_favor_id_saldo_favor_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.saldo_favor_id_saldo_favor_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: saldo_favor_id_saldo_favor_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.saldo_favor_id_saldo_favor_seq OWNED BY school.saldo_favor.id_saldo_favor;


--
-- Name: solvencia; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.solvencia (
    id_solvencia bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    id_inscripcion bigint NOT NULL,
    id_evaluacion bigint NOT NULL,
    fecha_generacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_corte date NOT NULL,
    saldo_corte numeric(12,2) NOT NULL,
    estado school.estado_solvencia NOT NULL,
    codigo_verificacion character varying(100) NOT NULL,
    observaciones text,
    CONSTRAINT ck_solvencia_saldo CHECK ((saldo_corte >= (0)::numeric))
);


--
-- Name: solvencia_id_solvencia_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.solvencia_id_solvencia_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: solvencia_id_solvencia_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.solvencia_id_solvencia_seq OWNED BY school.solvencia.id_solvencia;


--
-- Name: tipo_documento; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.tipo_documento (
    id_tipo_documento bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    obligatorio boolean DEFAULT false NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: tipo_documento_id_tipo_documento_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.tipo_documento_id_tipo_documento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipo_documento_id_tipo_documento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.tipo_documento_id_tipo_documento_seq OWNED BY school.tipo_documento.id_tipo_documento;


--
-- Name: usuario; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.usuario (
    id_usuario bigint NOT NULL,
    id_empleado bigint,
    username character varying(80) NOT NULL,
    password_hash text NOT NULL,
    estado school.estado_usuario DEFAULT 'ACTIVO'::school.estado_usuario NOT NULL,
    ultimo_acceso timestamp without time zone,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: school; Owner: -
--

CREATE SEQUENCE school.usuario_id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: -
--

ALTER SEQUENCE school.usuario_id_usuario_seq OWNED BY school.usuario.id_usuario;


--
-- Name: usuario_rol; Type: TABLE; Schema: school; Owner: -
--

CREATE TABLE school.usuario_rol (
    id_usuario bigint NOT NULL,
    id_rol bigint NOT NULL
);


--
-- Name: vw_saldo_obligaciones; Type: VIEW; Schema: school; Owner: -
--

CREATE VIEW school.vw_saldo_obligaciones AS
SELECT
    NULL::bigint AS id_obligacion,
    NULL::bigint AS id_inscripcion,
    NULL::character varying(150) AS concepto,
    NULL::character varying(20) AS periodo,
    NULL::date AS fecha_vencimiento,
    NULL::numeric(12,2) AS monto_bruto,
    NULL::numeric(12,2) AS monto_descuento,
    NULL::numeric(12,2) AS monto_beca,
    NULL::numeric(12,2) AS monto_neto,
    NULL::numeric AS total_pagado,
    NULL::numeric AS saldo;


--
-- Name: vw_estudiantes_insolventes; Type: VIEW; Schema: school; Owner: -
--

CREATE VIEW school.vw_estudiantes_insolventes AS
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


--
-- Name: vw_dashboard_financiero; Type: VIEW; Schema: school; Owner: -
--

CREATE VIEW school.vw_dashboard_financiero AS
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


--
-- Name: vw_deuda_por_estudiante; Type: VIEW; Schema: school; Owner: -
--

CREATE VIEW school.vw_deuda_por_estudiante AS
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


--
-- Name: vw_deuda_por_grado; Type: VIEW; Schema: school; Owner: -
--

CREATE VIEW school.vw_deuda_por_grado AS
 SELECT g.id_grado,
    g.nombre AS grado,
    count(DISTINCT i.id_estudiante) AS cantidad_estudiantes,
    COALESCE(sum(v.saldo), (0)::numeric) AS deuda_total
   FROM ((school.grado g
     JOIN school.inscripcion i ON ((i.id_grado = g.id_grado)))
     JOIN school.vw_saldo_obligaciones v ON ((v.id_inscripcion = i.id_inscripcion)))
  WHERE (i.estado = 'ACTIVA'::school.estado_inscripcion)
  GROUP BY g.id_grado, g.nombre;


--
-- Name: vw_estado_cuenta_estudiante; Type: VIEW; Schema: school; Owner: -
--

CREATE VIEW school.vw_estado_cuenta_estudiante AS
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


--
-- Name: aplicacion_pago id_aplicacion; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.aplicacion_pago ALTER COLUMN id_aplicacion SET DEFAULT nextval('school.aplicacion_pago_id_aplicacion_seq'::regclass);


--
-- Name: auditoria id_auditoria; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.auditoria ALTER COLUMN id_auditoria SET DEFAULT nextval('school.auditoria_id_auditoria_seq'::regclass);


--
-- Name: beca id_beca; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.beca ALTER COLUMN id_beca SET DEFAULT nextval('school.beca_id_beca_seq'::regclass);


--
-- Name: beca_estudiante id_beca_estudiante; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.beca_estudiante ALTER COLUMN id_beca_estudiante SET DEFAULT nextval('school.beca_estudiante_id_beca_estudiante_seq'::regclass);


--
-- Name: cambio_carrera id_cambio; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.cambio_carrera ALTER COLUMN id_cambio SET DEFAULT nextval('school.cambio_carrera_id_cambio_seq'::regclass);


--
-- Name: carrera id_carrera; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera ALTER COLUMN id_carrera SET DEFAULT nextval('school.carrera_id_carrera_seq'::regclass);


--
-- Name: carrera_ciclo id_carrera_ciclo; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera_ciclo ALTER COLUMN id_carrera_ciclo SET DEFAULT nextval('school.carrera_ciclo_id_carrera_ciclo_seq'::regclass);


--
-- Name: ciclo_escolar id_ciclo; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.ciclo_escolar ALTER COLUMN id_ciclo SET DEFAULT nextval('school.ciclo_escolar_id_ciclo_seq'::regclass);


--
-- Name: contacto id_contacto; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.contacto ALTER COLUMN id_contacto SET DEFAULT nextval('school.contacto_id_contacto_seq'::regclass);


--
-- Name: descuento id_descuento; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.descuento ALTER COLUMN id_descuento SET DEFAULT nextval('school.descuento_id_descuento_seq'::regclass);


--
-- Name: descuento_obligacion id_descuento_obligacion; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.descuento_obligacion ALTER COLUMN id_descuento_obligacion SET DEFAULT nextval('school.descuento_obligacion_id_descuento_obligacion_seq'::regclass);


--
-- Name: documento_expediente id_documento; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.documento_expediente ALTER COLUMN id_documento SET DEFAULT nextval('school.documento_expediente_id_documento_seq'::regclass);


--
-- Name: empleado id_empleado; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.empleado ALTER COLUMN id_empleado SET DEFAULT nextval('school.empleado_id_empleado_seq'::regclass);


--
-- Name: estudiante id_estudiante; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.estudiante ALTER COLUMN id_estudiante SET DEFAULT nextval('school.estudiante_id_estudiante_seq'::regclass);


--
-- Name: evaluacion id_evaluacion; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.evaluacion ALTER COLUMN id_evaluacion SET DEFAULT nextval('school.evaluacion_id_evaluacion_seq'::regclass);


--
-- Name: expediente id_expediente; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.expediente ALTER COLUMN id_expediente SET DEFAULT nextval('school.expediente_id_expediente_seq'::regclass);


--
-- Name: grado id_grado; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.grado ALTER COLUMN id_grado SET DEFAULT nextval('school.grado_id_grado_seq'::regclass);


--
-- Name: inscripcion id_inscripcion; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.inscripcion ALTER COLUMN id_inscripcion SET DEFAULT nextval('school.inscripcion_id_inscripcion_seq'::regclass);


--
-- Name: movimiento_saldo id_movimiento; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.movimiento_saldo ALTER COLUMN id_movimiento SET DEFAULT nextval('school.movimiento_saldo_id_movimiento_seq'::regclass);


--
-- Name: notificacion id_notificacion; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.notificacion ALTER COLUMN id_notificacion SET DEFAULT nextval('school.notificacion_id_notificacion_seq'::regclass);


--
-- Name: notificacion_destinatario id_destinatario; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.notificacion_destinatario ALTER COLUMN id_destinatario SET DEFAULT nextval('school.notificacion_destinatario_id_destinatario_seq'::regclass);


--
-- Name: obligacion id_obligacion; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.obligacion ALTER COLUMN id_obligacion SET DEFAULT nextval('school.obligacion_id_obligacion_seq'::regclass);


--
-- Name: pago id_pago; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.pago ALTER COLUMN id_pago SET DEFAULT nextval('school.pago_id_pago_seq'::regclass);


--
-- Name: permiso id_permiso; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.permiso ALTER COLUMN id_permiso SET DEFAULT nextval('school.permiso_id_permiso_seq'::regclass);


--
-- Name: precio_carrera id_precio; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.precio_carrera ALTER COLUMN id_precio SET DEFAULT nextval('school.precio_carrera_id_precio_seq'::regclass);


--
-- Name: recibo id_recibo; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.recibo ALTER COLUMN id_recibo SET DEFAULT nextval('school.recibo_id_recibo_seq'::regclass);


--
-- Name: rol id_rol; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.rol ALTER COLUMN id_rol SET DEFAULT nextval('school.rol_id_rol_seq'::regclass);


--
-- Name: saldo_favor id_saldo_favor; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.saldo_favor ALTER COLUMN id_saldo_favor SET DEFAULT nextval('school.saldo_favor_id_saldo_favor_seq'::regclass);


--
-- Name: solvencia id_solvencia; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.solvencia ALTER COLUMN id_solvencia SET DEFAULT nextval('school.solvencia_id_solvencia_seq'::regclass);


--
-- Name: tipo_documento id_tipo_documento; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.tipo_documento ALTER COLUMN id_tipo_documento SET DEFAULT nextval('school.tipo_documento_id_tipo_documento_seq'::regclass);


--
-- Name: usuario id_usuario; Type: DEFAULT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('school.usuario_id_usuario_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: aplicacion_pago aplicacion_pago_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT aplicacion_pago_pkey PRIMARY KEY (id_aplicacion);


--
-- Name: auditoria auditoria_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id_auditoria);


--
-- Name: beca_estudiante beca_estudiante_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT beca_estudiante_pkey PRIMARY KEY (id_beca_estudiante);


--
-- Name: beca beca_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.beca
    ADD CONSTRAINT beca_pkey PRIMARY KEY (id_beca);


--
-- Name: cambio_carrera cambio_carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT cambio_carrera_pkey PRIMARY KEY (id_cambio);


--
-- Name: carrera_ciclo carrera_ciclo_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT carrera_ciclo_pkey PRIMARY KEY (id_carrera_ciclo);


--
-- Name: carrera carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera
    ADD CONSTRAINT carrera_pkey PRIMARY KEY (id_carrera);


--
-- Name: ciclo_escolar ciclo_escolar_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.ciclo_escolar
    ADD CONSTRAINT ciclo_escolar_pkey PRIMARY KEY (id_ciclo);


--
-- Name: contacto contacto_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.contacto
    ADD CONSTRAINT contacto_pkey PRIMARY KEY (id_contacto);


--
-- Name: descuento_obligacion descuento_obligacion_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT descuento_obligacion_pkey PRIMARY KEY (id_descuento_obligacion);


--
-- Name: descuento descuento_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.descuento
    ADD CONSTRAINT descuento_pkey PRIMARY KEY (id_descuento);


--
-- Name: documento_expediente documento_expediente_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT documento_expediente_pkey PRIMARY KEY (id_documento);


--
-- Name: empleado empleado_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.empleado
    ADD CONSTRAINT empleado_pkey PRIMARY KEY (id_empleado);


--
-- Name: estudiante estudiante_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT estudiante_pkey PRIMARY KEY (id_estudiante);


--
-- Name: evaluacion evaluacion_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.evaluacion
    ADD CONSTRAINT evaluacion_pkey PRIMARY KEY (id_evaluacion);


--
-- Name: expediente expediente_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT expediente_pkey PRIMARY KEY (id_expediente);


--
-- Name: grado grado_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT grado_pkey PRIMARY KEY (id_grado);


--
-- Name: inscripcion inscripcion_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT inscripcion_pkey PRIMARY KEY (id_inscripcion);


--
-- Name: movimiento_saldo movimiento_saldo_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT movimiento_saldo_pkey PRIMARY KEY (id_movimiento);


--
-- Name: notificacion_destinatario notificacion_destinatario_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT notificacion_destinatario_pkey PRIMARY KEY (id_destinatario);


--
-- Name: notificacion notificacion_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.notificacion
    ADD CONSTRAINT notificacion_pkey PRIMARY KEY (id_notificacion);


--
-- Name: obligacion obligacion_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT obligacion_pkey PRIMARY KEY (id_obligacion);


--
-- Name: pago pago_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.pago
    ADD CONSTRAINT pago_pkey PRIMARY KEY (id_pago);


--
-- Name: permiso permiso_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.permiso
    ADD CONSTRAINT permiso_pkey PRIMARY KEY (id_permiso);


--
-- Name: precio_carrera precio_carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.precio_carrera
    ADD CONSTRAINT precio_carrera_pkey PRIMARY KEY (id_precio);


--
-- Name: recibo recibo_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT recibo_pkey PRIMARY KEY (id_recibo);


--
-- Name: rol_permiso rol_permiso_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT rol_permiso_pkey PRIMARY KEY (id_rol, id_permiso);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- Name: saldo_favor saldo_favor_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.saldo_favor
    ADD CONSTRAINT saldo_favor_pkey PRIMARY KEY (id_saldo_favor);


--
-- Name: solvencia solvencia_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT solvencia_pkey PRIMARY KEY (id_solvencia);


--
-- Name: tipo_documento tipo_documento_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.tipo_documento
    ADD CONSTRAINT tipo_documento_pkey PRIMARY KEY (id_tipo_documento);


--
-- Name: aplicacion_pago uq_aplicacion_pago_obligacion; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT uq_aplicacion_pago_obligacion UNIQUE (id_pago, id_obligacion);


--
-- Name: beca uq_beca_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.beca
    ADD CONSTRAINT uq_beca_nombre UNIQUE (nombre);


--
-- Name: carrera_ciclo uq_carrera_ciclo; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT uq_carrera_ciclo UNIQUE (id_carrera, id_ciclo);


--
-- Name: carrera uq_carrera_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera
    ADD CONSTRAINT uq_carrera_nombre UNIQUE (nombre);


--
-- Name: ciclo_escolar uq_ciclo_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.ciclo_escolar
    ADD CONSTRAINT uq_ciclo_nombre UNIQUE (nombre);


--
-- Name: descuento uq_descuento_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.descuento
    ADD CONSTRAINT uq_descuento_nombre UNIQUE (nombre);


--
-- Name: estudiante uq_estudiante_codigo; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT uq_estudiante_codigo UNIQUE (codigo_estudiante);


--
-- Name: estudiante uq_estudiante_cui; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT uq_estudiante_cui UNIQUE (cui);


--
-- Name: expediente uq_expediente_estudiante; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT uq_expediente_estudiante UNIQUE (id_estudiante);


--
-- Name: grado uq_grado_carrera_ciclo_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT uq_grado_carrera_ciclo_nombre UNIQUE (id_carrera_ciclo, nombre);


--
-- Name: permiso uq_permiso_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.permiso
    ADD CONSTRAINT uq_permiso_nombre UNIQUE (nombre);


--
-- Name: recibo uq_recibo_codigo; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_codigo UNIQUE (codigo_verificacion);


--
-- Name: recibo uq_recibo_numero; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_numero UNIQUE (numero_recibo);


--
-- Name: recibo uq_recibo_pago; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_pago UNIQUE (id_pago);


--
-- Name: rol uq_rol_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.rol
    ADD CONSTRAINT uq_rol_nombre UNIQUE (nombre);


--
-- Name: solvencia uq_solvencia_codigo; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT uq_solvencia_codigo UNIQUE (codigo_verificacion);


--
-- Name: tipo_documento uq_tipo_documento_nombre; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.tipo_documento
    ADD CONSTRAINT uq_tipo_documento_nombre UNIQUE (nombre);


--
-- Name: usuario uq_usuario_empleado; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT uq_usuario_empleado UNIQUE (id_empleado);


--
-- Name: usuario uq_usuario_username; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT uq_usuario_username UNIQUE (username);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- Name: usuario_rol usuario_rol_pkey; Type: CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT usuario_rol_pkey PRIMARY KEY (id_usuario, id_rol);


--
-- Name: idx_aplicacion_obligacion; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_aplicacion_obligacion ON school.aplicacion_pago USING btree (id_obligacion);


--
-- Name: idx_aplicacion_pago; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_aplicacion_pago ON school.aplicacion_pago USING btree (id_pago);


--
-- Name: idx_auditoria_fecha; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_auditoria_fecha ON school.auditoria USING btree (fecha_evento);


--
-- Name: idx_auditoria_usuario; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_auditoria_usuario ON school.auditoria USING btree (id_usuario);


--
-- Name: idx_contacto_estudiante; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_contacto_estudiante ON school.contacto USING btree (id_estudiante);


--
-- Name: idx_documento_expediente; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_documento_expediente ON school.documento_expediente USING btree (id_expediente);


--
-- Name: idx_estudiante_activo; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_estudiante_activo ON school.estudiante USING btree (id_estudiante) WHERE (estado = 'ACTIVO'::school.estado_estudiante);


--
-- Name: idx_inscripcion_activa; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_inscripcion_activa ON school.inscripcion USING btree (id_estudiante) WHERE (estado = 'ACTIVA'::school.estado_inscripcion);


--
-- Name: idx_inscripcion_carrera_ciclo; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_inscripcion_carrera_ciclo ON school.inscripcion USING btree (id_carrera_ciclo);


--
-- Name: idx_inscripcion_estudiante; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_inscripcion_estudiante ON school.inscripcion USING btree (id_estudiante);


--
-- Name: idx_inscripcion_grado; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_inscripcion_grado ON school.inscripcion USING btree (id_grado);


--
-- Name: idx_movimiento_destino; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_movimiento_destino ON school.movimiento_saldo USING btree (id_inscripcion_destino);


--
-- Name: idx_movimiento_estudiante; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_movimiento_estudiante ON school.movimiento_saldo USING btree (id_estudiante);


--
-- Name: idx_movimiento_origen; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_movimiento_origen ON school.movimiento_saldo USING btree (id_inscripcion_origen);


--
-- Name: idx_obligacion_fecha_vencimiento; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_obligacion_fecha_vencimiento ON school.obligacion USING btree (fecha_vencimiento);


--
-- Name: idx_obligacion_inscripcion; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_obligacion_inscripcion ON school.obligacion USING btree (id_inscripcion);


--
-- Name: idx_obligacion_pendiente; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_obligacion_pendiente ON school.obligacion USING btree (id_inscripcion) WHERE (estado = ANY (ARRAY['PENDIENTE'::school.estado_obligacion, 'PARCIAL'::school.estado_obligacion]));


--
-- Name: idx_pago_estudiante; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_pago_estudiante ON school.pago USING btree (id_estudiante);


--
-- Name: idx_pago_fecha; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_pago_fecha ON school.pago USING btree (fecha_pago);


--
-- Name: idx_saldo_favor_estudiante; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_saldo_favor_estudiante ON school.saldo_favor USING btree (id_estudiante) WHERE ((estado)::text = 'ACTIVO'::text);


--
-- Name: idx_solvencia_estudiante; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_solvencia_estudiante ON school.solvencia USING btree (id_estudiante);


--
-- Name: idx_solvencia_evaluacion; Type: INDEX; Schema: school; Owner: -
--

CREATE INDEX idx_solvencia_evaluacion ON school.solvencia USING btree (id_evaluacion);


--
-- Name: uq_inscripcion_activa_estudiante_ciclo; Type: INDEX; Schema: school; Owner: -
--

CREATE UNIQUE INDEX uq_inscripcion_activa_estudiante_ciclo ON school.inscripcion USING btree (id_estudiante, id_carrera_ciclo) WHERE (estado = 'ACTIVA'::school.estado_inscripcion);


--
-- Name: uq_obligacion_mensualidad_periodo; Type: INDEX; Schema: school; Owner: -
--

CREATE UNIQUE INDEX uq_obligacion_mensualidad_periodo ON school.obligacion USING btree (id_inscripcion, periodo) WHERE ((tipo_obligacion)::text = 'MENSUALIDAD'::text);


--
-- Name: vw_saldo_obligaciones _RETURN; Type: RULE; Schema: school; Owner: -
--

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
    (o.monto_neto - COALESCE(sum(
        CASE
            WHEN (p.estado = 'CONFIRMADO'::school.estado_pago) THEN ap.monto_aplicado
            ELSE (0)::numeric
        END), (0)::numeric)) AS saldo
   FROM ((school.obligacion o
     LEFT JOIN school.aplicacion_pago ap ON ((ap.id_obligacion = o.id_obligacion)))
     LEFT JOIN school.pago p ON ((p.id_pago = ap.id_pago)))
  GROUP BY o.id_obligacion;


--
-- Name: aplicacion_pago trg_actualizar_estado_obligacion; Type: TRIGGER; Schema: school; Owner: -
--

CREATE TRIGGER trg_actualizar_estado_obligacion AFTER INSERT OR DELETE OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_trigger_actualizar_obligacion();


--
-- Name: pago trg_recalcular_obligaciones_pago_anulado; Type: TRIGGER; Schema: school; Owner: -
--

CREATE TRIGGER trg_recalcular_obligaciones_pago_anulado AFTER UPDATE ON school.pago FOR EACH ROW EXECUTE FUNCTION school.fn_recalcular_obligaciones_pago_anulado();


--
-- Name: aplicacion_pago trg_validar_aplicacion_pago; Type: TRIGGER; Schema: school; Owner: -
--

CREATE TRIGGER trg_validar_aplicacion_pago BEFORE INSERT OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_validar_aplicacion_pago();


--
-- Name: descuento_obligacion trg_validar_descuentos_obligacion; Type: TRIGGER; Schema: school; Owner: -
--

CREATE TRIGGER trg_validar_descuentos_obligacion BEFORE INSERT OR UPDATE ON school.descuento_obligacion FOR EACH ROW EXECUTE FUNCTION school.fn_validar_descuentos_obligacion();


--
-- Name: inscripcion trg_validar_grado_inscripcion; Type: TRIGGER; Schema: school; Owner: -
--

CREATE TRIGGER trg_validar_grado_inscripcion BEFORE INSERT OR UPDATE ON school.inscripcion FOR EACH ROW EXECUTE FUNCTION school.fn_validar_grado_inscripcion();


--
-- Name: movimiento_saldo trg_validar_movimiento_saldo; Type: TRIGGER; Schema: school; Owner: -
--

CREATE TRIGGER trg_validar_movimiento_saldo BEFORE INSERT OR UPDATE ON school.movimiento_saldo FOR EACH ROW EXECUTE FUNCTION school.fn_validar_movimiento_saldo();


--
-- Name: aplicacion_pago trg_validar_propietario_pago_obligacion; Type: TRIGGER; Schema: school; Owner: -
--

CREATE TRIGGER trg_validar_propietario_pago_obligacion BEFORE INSERT OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_validar_propietario_pago_obligacion();


--
-- Name: aplicacion_pago fk_aplicacion_obligacion; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT fk_aplicacion_obligacion FOREIGN KEY (id_obligacion) REFERENCES school.obligacion(id_obligacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: aplicacion_pago fk_aplicacion_pago; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT fk_aplicacion_pago FOREIGN KEY (id_pago) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: auditoria fk_auditoria_usuario; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.auditoria
    ADD CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES school.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: beca_estudiante fk_beca_estudiante_beca; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT fk_beca_estudiante_beca FOREIGN KEY (id_beca) REFERENCES school.beca(id_beca) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: beca_estudiante fk_beca_estudiante_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT fk_beca_estudiante_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: cambio_carrera fk_cambio_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: cambio_carrera fk_cambio_inscripcion_destino; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_inscripcion_destino FOREIGN KEY (id_inscripcion_destino) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: cambio_carrera fk_cambio_inscripcion_origen; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_inscripcion_origen FOREIGN KEY (id_inscripcion_origen) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: carrera_ciclo fk_carrera_ciclo_carrera; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT fk_carrera_ciclo_carrera FOREIGN KEY (id_carrera) REFERENCES school.carrera(id_carrera) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: carrera_ciclo fk_carrera_ciclo_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT fk_carrera_ciclo_ciclo FOREIGN KEY (id_ciclo) REFERENCES school.ciclo_escolar(id_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: contacto fk_contacto_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.contacto
    ADD CONSTRAINT fk_contacto_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: descuento_obligacion fk_descuento_obligacion_descuento; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT fk_descuento_obligacion_descuento FOREIGN KEY (id_descuento) REFERENCES school.descuento(id_descuento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: descuento_obligacion fk_descuento_obligacion_obligacion; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT fk_descuento_obligacion_obligacion FOREIGN KEY (id_obligacion) REFERENCES school.obligacion(id_obligacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: documento_expediente fk_documento_expediente; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT fk_documento_expediente FOREIGN KEY (id_expediente) REFERENCES school.expediente(id_expediente) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: documento_expediente fk_documento_tipo; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT fk_documento_tipo FOREIGN KEY (id_tipo_documento) REFERENCES school.tipo_documento(id_tipo_documento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: evaluacion fk_evaluacion_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.evaluacion
    ADD CONSTRAINT fk_evaluacion_ciclo FOREIGN KEY (id_ciclo) REFERENCES school.ciclo_escolar(id_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: expediente fk_expediente_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT fk_expediente_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: grado fk_grado_carrera_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT fk_grado_carrera_ciclo FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: inscripcion fk_inscripcion_carrera_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT fk_inscripcion_carrera_ciclo FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: inscripcion fk_inscripcion_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT fk_inscripcion_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: inscripcion fk_inscripcion_grado; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT fk_inscripcion_grado FOREIGN KEY (id_grado) REFERENCES school.grado(id_grado) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: movimiento_saldo fk_movimiento_destino; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_destino FOREIGN KEY (id_inscripcion_destino) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: movimiento_saldo fk_movimiento_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: movimiento_saldo fk_movimiento_origen; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_origen FOREIGN KEY (id_inscripcion_origen) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: notificacion_destinatario fk_notificacion_contacto; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT fk_notificacion_contacto FOREIGN KEY (id_contacto) REFERENCES school.contacto(id_contacto) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: notificacion_destinatario fk_notificacion_destinatario; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT fk_notificacion_destinatario FOREIGN KEY (id_notificacion) REFERENCES school.notificacion(id_notificacion) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: obligacion fk_obligacion_inscripcion; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT fk_obligacion_inscripcion FOREIGN KEY (id_inscripcion) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: obligacion fk_obligacion_precio; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT fk_obligacion_precio FOREIGN KEY (id_precio) REFERENCES school.precio_carrera(id_precio) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: pago fk_pago_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.pago
    ADD CONSTRAINT fk_pago_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: precio_carrera fk_precio_carrera_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.precio_carrera
    ADD CONSTRAINT fk_precio_carrera_ciclo FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: recibo fk_recibo_pago; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT fk_recibo_pago FOREIGN KEY (id_pago) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rol_permiso fk_rol_permiso_permiso; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT fk_rol_permiso_permiso FOREIGN KEY (id_permiso) REFERENCES school.permiso(id_permiso) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rol_permiso fk_rol_permiso_rol; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT fk_rol_permiso_rol FOREIGN KEY (id_rol) REFERENCES school.rol(id_rol) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: saldo_favor fk_saldo_favor_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.saldo_favor
    ADD CONSTRAINT fk_saldo_favor_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: saldo_favor fk_saldo_favor_pago; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.saldo_favor
    ADD CONSTRAINT fk_saldo_favor_pago FOREIGN KEY (id_pago_origen) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: solvencia fk_solvencia_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: solvencia fk_solvencia_evaluacion; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_evaluacion FOREIGN KEY (id_evaluacion) REFERENCES school.evaluacion(id_evaluacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: solvencia fk_solvencia_inscripcion; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_inscripcion FOREIGN KEY (id_inscripcion) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: usuario fk_usuario_empleado; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT fk_usuario_empleado FOREIGN KEY (id_empleado) REFERENCES school.empleado(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: usuario_rol fk_usuario_rol_rol; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_rol FOREIGN KEY (id_rol) REFERENCES school.rol(id_rol) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: usuario_rol fk_usuario_rol_usuario; Type: FK CONSTRAINT; Schema: school; Owner: -
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_usuario FOREIGN KEY (id_usuario) REFERENCES school.usuario(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict lfKILKxCngeHCCqEUhrsTPDKY0SaNMGeYYdkPVcCvDomQO13xl8mogc9DJYbhWM

