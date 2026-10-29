--
-- PostgreSQL database dump
--

\restrict rGFKUzRb1wSZn96QRbGXinkhnINTB4Tkdz17gHAlUWlEtEs3GObSziPnMdK32fG

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-09-29 08:33:22

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
-- TOC entry 6 (class 2615 OID 26729)
-- Name: school; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA school;


ALTER SCHEMA school OWNER TO postgres;

--
-- TOC entry 952 (class 1247 OID 26737)
-- Name: estado_beca; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_beca AS ENUM (
    'PENDIENTE',
    'ACTIVA',
    'FINALIZADA',
    'CANCELADA'
);


ALTER TYPE school.estado_beca OWNER TO postgres;

--
-- TOC entry 1060 (class 1247 OID 27388)
-- Name: estado_cambio_carrera; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_cambio_carrera AS ENUM (
    'SOLICITADO',
    'APROBADO',
    'RECHAZADO',
    'CANCELADO'
);


ALTER TYPE school.estado_cambio_carrera OWNER TO postgres;

--
-- TOC entry 961 (class 1247 OID 26781)
-- Name: estado_ciclo; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_ciclo AS ENUM (
    'PLANIFICADO',
    'ACTIVO',
    'CERRADO'
);


ALTER TYPE school.estado_ciclo OWNER TO postgres;

--
-- TOC entry 973 (class 1247 OID 26838)
-- Name: estado_estudiante; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_estudiante AS ENUM (
    'ACTIVO',
    'INACTIVO',
    'RETIRADO',
    'EGRESADO'
);


ALTER TYPE school.estado_estudiante OWNER TO postgres;

--
-- TOC entry 1054 (class 1247 OID 27338)
-- Name: estado_inscripcion; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_inscripcion AS ENUM (
    'ACTIVA',
    'FINALIZADA',
    'CANCELADA',
    'RETIRADA'
);


ALTER TYPE school.estado_inscripcion OWNER TO postgres;

--
-- TOC entry 1069 (class 1247 OID 27436)
-- Name: estado_movimiento_saldo; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_movimiento_saldo AS ENUM (
    'PENDIENTE',
    'APLICADO',
    'ANULADO'
);


ALTER TYPE school.estado_movimiento_saldo OWNER TO postgres;

--
-- TOC entry 1075 (class 1247 OID 27478)
-- Name: estado_obligacion; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_obligacion AS ENUM (
    'PENDIENTE',
    'PARCIAL',
    'PAGADA',
    'ANULADA'
);


ALTER TYPE school.estado_obligacion OWNER TO postgres;

--
-- TOC entry 1009 (class 1247 OID 27052)
-- Name: estado_pago; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_pago AS ENUM (
    'PENDIENTE',
    'CONFIRMADO',
    'ANULADO'
);


ALTER TYPE school.estado_pago OWNER TO postgres;

--
-- TOC entry 1081 (class 1247 OID 27529)
-- Name: estado_solvencia; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_solvencia AS ENUM (
    'SOLVENTE',
    'INSOLVENTE'
);


ALTER TYPE school.estado_solvencia OWNER TO postgres;

--
-- TOC entry 1018 (class 1247 OID 27104)
-- Name: estado_usuario; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_usuario AS ENUM (
    'ACTIVO',
    'INACTIVO',
    'BLOQUEADO'
);


ALTER TYPE school.estado_usuario OWNER TO postgres;

--
-- TOC entry 1006 (class 1247 OID 27041)
-- Name: metodo_pago; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.metodo_pago AS ENUM (
    'EFECTIVO',
    'TRANSFERENCIA',
    'DEPOSITO',
    'TARJETA',
    'OTRO'
);


ALTER TYPE school.metodo_pago OWNER TO postgres;

--
-- TOC entry 1051 (class 1247 OID 27330)
-- Name: tipo_inscripcion; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.tipo_inscripcion AS ENUM (
    'NUEVA',
    'REINSCRIPCION',
    'TRASLADO'
);


ALTER TYPE school.tipo_inscripcion OWNER TO postgres;

--
-- TOC entry 1066 (class 1247 OID 27427)
-- Name: tipo_movimiento_saldo; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.tipo_movimiento_saldo AS ENUM (
    'TRASLADO_SALDO',
    'AJUSTE',
    'DEVOLUCION',
    'COMPENSACION'
);


ALTER TYPE school.tipo_movimiento_saldo OWNER TO postgres;

--
-- TOC entry 1036 (class 1247 OID 27226)
-- Name: tipo_precio; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.tipo_precio AS ENUM (
    'INSCRIPCION',
    'MENSUALIDAD',
    'OTRO'
);


ALTER TYPE school.tipo_precio OWNER TO postgres;

--
-- TOC entry 294 (class 1255 OID 27627)
-- Name: fn_actualizar_estado_obligacion(bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_actualizar_estado_obligacion(p_id_obligacion bigint) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_actualizar_estado_obligacion(p_id_obligacion bigint) OWNER TO postgres;

--
-- TOC entry 299 (class 1255 OID 27628)
-- Name: fn_anular_pago(bigint, text, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_anular_pago(p_id_pago bigint, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_anular_pago(p_id_pago bigint, p_motivo text, p_id_usuario bigint) OWNER TO postgres;

--
-- TOC entry 327 (class 1255 OID 33914)
-- Name: fn_aplicar_beca_estudiante_obligacion(bigint, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_aplicar_beca_estudiante_obligacion(p_id_beca_estudiante bigint, p_id_obligacion bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
    AS $$
        DECLARE
            v_id_estudiante_beca BIGINT;
            v_id_estudiante_obligacion BIGINT;

            v_estado_beca school.estado_beca;

            v_asignacion_inicio DATE;
            v_asignacion_fin DATE;

            v_beca_inicio DATE;
            v_beca_fin DATE;

            v_fecha_referencia DATE;

            v_porcentaje NUMERIC(5,2);
            v_monto_beca NUMERIC(12,2);

            v_estado_obligacion school.estado_obligacion;
            v_total_pagado NUMERIC(12,2);

            v_id_beca_obligacion BIGINT;
        BEGIN

            SELECT
                be.id_estudiante,
                b.estado,
                be.fecha_inicio,
                be.fecha_fin,
                b.fecha_inicio,
                b.fecha_fin,
                COALESCE(
                    be.porcentaje_aplicado,
                    b.porcentaje
                )
            INTO
                v_id_estudiante_beca,
                v_estado_beca,
                v_asignacion_inicio,
                v_asignacion_fin,
                v_beca_inicio,
                v_beca_fin,
                v_porcentaje
            FROM beca_estudiante be
            JOIN beca b
                ON b.id_beca = be.id_beca
            WHERE be.id_beca_estudiante =
                p_id_beca_estudiante
            FOR UPDATE OF be, b;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'La asignación de beca no existe.';
            END IF;

            IF v_estado_beca <> 'ACTIVA' THEN
                RAISE EXCEPTION
                    'La beca no está activa.';
            END IF;

            SELECT
                i.id_estudiante,
                o.estado,
                COALESCE(
                    o.fecha_vencimiento,
                    CURRENT_DATE
                )
            INTO
                v_id_estudiante_obligacion,
                v_estado_obligacion,
                v_fecha_referencia
            FROM obligacion o
            JOIN inscripcion i
                ON i.id_inscripcion =
                o.id_inscripcion
            WHERE o.id_obligacion =
                p_id_obligacion
            FOR UPDATE OF o;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'La obligación no existe.';
            END IF;

            IF v_id_estudiante_beca
            <> v_id_estudiante_obligacion THEN
                RAISE EXCEPTION
                    'La obligación no pertenece al estudiante de la beca.';
            END IF;

            IF v_estado_obligacion <> 'PENDIENTE' THEN
                RAISE EXCEPTION
                    'La beca solo puede aplicarse a una obligación pendiente.';
            END IF;

            SELECT COALESCE(
                (
                    SELECT total_pagado
                    FROM vw_saldo_obligaciones
                    WHERE id_obligacion =
                        p_id_obligacion
                ),
                0
            )
            INTO v_total_pagado;

            IF v_total_pagado > 0 THEN
                RAISE EXCEPTION
                    'No puede aplicarse una beca a una obligación que ya recibió pagos.';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM beca_obligacion
                WHERE id_obligacion =
                    p_id_obligacion
            ) THEN
                RAISE EXCEPTION
                    'La obligación ya tiene una beca aplicada.';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM obligacion
                WHERE id_obligacion =
                    p_id_obligacion
                AND monto_beca > 0
            ) THEN
                RAISE EXCEPTION
                    'La obligación ya contiene un monto de beca sin trazabilidad.';
            END IF;

            IF v_fecha_referencia
            < v_asignacion_inicio THEN
                RAISE EXCEPTION
                    'La obligación es anterior a la vigencia de la asignación de beca.';
            END IF;

            IF v_asignacion_fin IS NOT NULL
            AND v_fecha_referencia
                > v_asignacion_fin THEN
                RAISE EXCEPTION
                    'La obligación está fuera de la vigencia de la asignación de beca.';
            END IF;

            IF v_beca_inicio IS NOT NULL
            AND v_fecha_referencia
                < v_beca_inicio THEN
                RAISE EXCEPTION
                    'La beca aún no estaba vigente.';
            END IF;

            IF v_beca_fin IS NOT NULL
            AND v_fecha_referencia
                > v_beca_fin THEN
                RAISE EXCEPTION
                    'La beca ya no estaba vigente.';
            END IF;

            PERFORM fn_aplicar_beca_obligacion(
                p_id_obligacion,
                v_porcentaje
            );

            SELECT monto_beca
            INTO v_monto_beca
            FROM obligacion
            WHERE id_obligacion =
                p_id_obligacion;

            INSERT INTO beca_obligacion (
                id_beca_estudiante,
                id_obligacion,
                porcentaje_aplicado,
                monto_aplicado
            )
            VALUES (
                p_id_beca_estudiante,
                p_id_obligacion,
                v_porcentaje,
                v_monto_beca
            )
            RETURNING id_beca_obligacion
            INTO v_id_beca_obligacion;

            RETURN v_id_beca_obligacion;

        END;
        $$;


ALTER FUNCTION school.fn_aplicar_beca_estudiante_obligacion(p_id_beca_estudiante bigint, p_id_obligacion bigint) OWNER TO postgres;

--
-- TOC entry 307 (class 1255 OID 27629)
-- Name: fn_aplicar_beca_obligacion(bigint, numeric); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_aplicar_beca_obligacion(p_id_obligacion bigint, p_porcentaje numeric) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_aplicar_beca_obligacion(p_id_obligacion bigint, p_porcentaje numeric) OWNER TO postgres;

--
-- TOC entry 308 (class 1255 OID 27630)
-- Name: fn_aplicar_descuento_obligacion(bigint, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_aplicar_descuento_obligacion(p_id_obligacion bigint, p_id_descuento bigint) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_aplicar_descuento_obligacion(p_id_obligacion bigint, p_id_descuento bigint) OWNER TO postgres;

--
-- TOC entry 310 (class 1255 OID 27632)
-- Name: fn_aplicar_pago(bigint, bigint, numeric); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_aplicar_pago(p_id_pago bigint, p_id_obligacion bigint, p_monto numeric) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_aplicar_pago(p_id_pago bigint, p_id_obligacion bigint, p_monto numeric) OWNER TO postgres;

--
-- TOC entry 311 (class 1255 OID 27633)
-- Name: fn_aplicar_saldo_favor(bigint, bigint, numeric); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_aplicar_saldo_favor(p_id_saldo_favor bigint, p_id_obligacion bigint, p_monto numeric) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_aplicar_saldo_favor(p_id_saldo_favor bigint, p_id_obligacion bigint, p_monto numeric) OWNER TO postgres;

--
-- TOC entry 293 (class 1255 OID 27634)
-- Name: fn_calcular_saldo_corte(bigint, date); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_calcular_saldo_corte(p_id_inscripcion bigint, p_fecha_corte date) RETURNS numeric
    LANGUAGE sql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_calcular_saldo_corte(p_id_inscripcion bigint, p_fecha_corte date) OWNER TO postgres;

--
-- TOC entry 312 (class 1255 OID 27635)
-- Name: fn_cambiar_carrera(bigint, bigint, bigint, bigint, text, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_cambiar_carrera(p_id_estudiante bigint, p_id_inscripcion_origen bigint, p_id_carrera_ciclo_destino bigint, p_id_grado_destino bigint, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_cambiar_carrera(p_id_estudiante bigint, p_id_inscripcion_origen bigint, p_id_carrera_ciclo_destino bigint, p_id_grado_destino bigint, p_motivo text, p_id_usuario bigint) OWNER TO postgres;

--
-- TOC entry 313 (class 1255 OID 27636)
-- Name: fn_generar_obligaciones_mensuales(bigint, bigint, date, integer); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_generar_obligaciones_mensuales(p_id_inscripcion bigint, p_id_precio bigint, p_fecha_inicio date, p_cantidad_meses integer) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_generar_obligaciones_mensuales(p_id_inscripcion bigint, p_id_precio bigint, p_fecha_inicio date, p_cantidad_meses integer) OWNER TO postgres;

--
-- TOC entry 314 (class 1255 OID 27637)
-- Name: fn_generar_recibo(bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_generar_recibo(p_id_pago bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_generar_recibo(p_id_pago bigint) OWNER TO postgres;

--
-- TOC entry 315 (class 1255 OID 27638)
-- Name: fn_generar_solvencia(bigint, bigint, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_generar_solvencia(p_id_estudiante bigint, p_id_inscripcion bigint, p_id_evaluacion bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_generar_solvencia(p_id_estudiante bigint, p_id_inscripcion bigint, p_id_evaluacion bigint) OWNER TO postgres;

--
-- TOC entry 316 (class 1255 OID 27639)
-- Name: fn_recalcular_obligaciones_pago_anulado(); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_recalcular_obligaciones_pago_anulado() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_recalcular_obligaciones_pago_anulado() OWNER TO postgres;

--
-- TOC entry 317 (class 1255 OID 27640)
-- Name: fn_registrar_auditoria(bigint, character varying, character varying, character varying, bigint, text, jsonb, jsonb); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_registrar_auditoria(p_id_usuario bigint, p_modulo character varying, p_accion character varying, p_tabla character varying, p_id_registro bigint, p_descripcion text, p_datos_anteriores jsonb DEFAULT NULL::jsonb, p_datos_nuevos jsonb DEFAULT NULL::jsonb) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_registrar_auditoria(p_id_usuario bigint, p_modulo character varying, p_accion character varying, p_tabla character varying, p_id_registro bigint, p_descripcion text, p_datos_anteriores jsonb, p_datos_nuevos jsonb) OWNER TO postgres;

--
-- TOC entry 318 (class 1255 OID 27641)
-- Name: fn_registrar_pago(bigint, numeric, school.metodo_pago, character varying, text, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_registrar_pago(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying DEFAULT NULL::character varying, p_observaciones text DEFAULT NULL::text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_registrar_pago(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying, p_observaciones text, p_id_usuario bigint) OWNER TO postgres;

--
-- TOC entry 319 (class 1255 OID 27642)
-- Name: fn_registrar_pago_automatico(bigint, numeric, school.metodo_pago, character varying, text, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_registrar_pago_automatico(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying DEFAULT NULL::character varying, p_observaciones text DEFAULT NULL::text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_registrar_pago_automatico(p_id_estudiante bigint, p_monto numeric, p_metodo school.metodo_pago, p_referencia character varying, p_observaciones text, p_id_usuario bigint) OWNER TO postgres;

--
-- TOC entry 309 (class 1255 OID 27631)
-- Name: fn_saldo_disponible_pago(bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_saldo_disponible_pago(p_id_pago bigint) RETURNS numeric
    LANGUAGE sql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_saldo_disponible_pago(p_id_pago bigint) OWNER TO postgres;

--
-- TOC entry 320 (class 1255 OID 27643)
-- Name: fn_trasladar_saldo(bigint, bigint, bigint, numeric, text, bigint); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_trasladar_saldo(p_id_estudiante bigint, p_inscripcion_origen bigint, p_inscripcion_destino bigint, p_monto numeric, p_motivo text, p_id_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_trasladar_saldo(p_id_estudiante bigint, p_inscripcion_origen bigint, p_inscripcion_destino bigint, p_monto numeric, p_motivo text, p_id_usuario bigint) OWNER TO postgres;

--
-- TOC entry 321 (class 1255 OID 27644)
-- Name: fn_trigger_actualizar_obligacion(); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_trigger_actualizar_obligacion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_trigger_actualizar_obligacion() OWNER TO postgres;

--
-- TOC entry 322 (class 1255 OID 27645)
-- Name: fn_validar_aplicacion_pago(); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_validar_aplicacion_pago() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_validar_aplicacion_pago() OWNER TO postgres;

--
-- TOC entry 323 (class 1255 OID 27646)
-- Name: fn_validar_descuentos_obligacion(); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_validar_descuentos_obligacion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_validar_descuentos_obligacion() OWNER TO postgres;

--
-- TOC entry 324 (class 1255 OID 27647)
-- Name: fn_validar_grado_inscripcion(); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_validar_grado_inscripcion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_validar_grado_inscripcion() OWNER TO postgres;

--
-- TOC entry 325 (class 1255 OID 27648)
-- Name: fn_validar_movimiento_saldo(); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_validar_movimiento_saldo() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_validar_movimiento_saldo() OWNER TO postgres;

--
-- TOC entry 326 (class 1255 OID 27649)
-- Name: fn_validar_propietario_pago_obligacion(); Type: FUNCTION; Schema: school; Owner: postgres
--

CREATE FUNCTION school.fn_validar_propietario_pago_obligacion() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'school', 'pg_catalog'
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


ALTER FUNCTION school.fn_validar_propietario_pago_obligacion() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 26730)
-- Name: alembic_version; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE school.alembic_version OWNER TO postgres;

--
-- TOC entry 282 (class 1259 OID 27573)
-- Name: aplicacion_pago; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.aplicacion_pago (
    id_aplicacion bigint NOT NULL,
    id_pago bigint NOT NULL,
    id_obligacion bigint NOT NULL,
    monto_aplicado numeric(12,2) NOT NULL,
    fecha_aplicacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_aplicacion_monto CHECK ((monto_aplicado > (0)::numeric))
);


ALTER TABLE school.aplicacion_pago OWNER TO postgres;

--
-- TOC entry 281 (class 1259 OID 27572)
-- Name: aplicacion_pago_id_aplicacion_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.aplicacion_pago_id_aplicacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.aplicacion_pago_id_aplicacion_seq OWNER TO postgres;

--
-- TOC entry 5638 (class 0 OID 0)
-- Dependencies: 281
-- Name: aplicacion_pago_id_aplicacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.aplicacion_pago_id_aplicacion_seq OWNED BY school.aplicacion_pago.id_aplicacion;


--
-- TOC entry 257 (class 1259 OID 27137)
-- Name: auditoria; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.auditoria OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 27136)
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.auditoria_id_auditoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.auditoria_id_auditoria_seq OWNER TO postgres;

--
-- TOC entry 5639 (class 0 OID 0)
-- Dependencies: 256
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.auditoria_id_auditoria_seq OWNED BY school.auditoria.id_auditoria;


--
-- TOC entry 222 (class 1259 OID 26746)
-- Name: beca; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.beca OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 26932)
-- Name: beca_estudiante; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.beca_estudiante OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 26931)
-- Name: beca_estudiante_id_beca_estudiante_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.beca_estudiante_id_beca_estudiante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.beca_estudiante_id_beca_estudiante_seq OWNER TO postgres;

--
-- TOC entry 5640 (class 0 OID 0)
-- Dependencies: 241
-- Name: beca_estudiante_id_beca_estudiante_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.beca_estudiante_id_beca_estudiante_seq OWNED BY school.beca_estudiante.id_beca_estudiante;


--
-- TOC entry 221 (class 1259 OID 26745)
-- Name: beca_id_beca_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.beca_id_beca_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.beca_id_beca_seq OWNER TO postgres;

--
-- TOC entry 5641 (class 0 OID 0)
-- Dependencies: 221
-- Name: beca_id_beca_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.beca_id_beca_seq OWNED BY school.beca.id_beca;


--
-- TOC entry 292 (class 1259 OID 33886)
-- Name: beca_obligacion; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.beca_obligacion (
    id_beca_obligacion bigint NOT NULL,
    id_beca_estudiante bigint NOT NULL,
    id_obligacion bigint NOT NULL,
    porcentaje_aplicado numeric(5,2) NOT NULL,
    monto_aplicado numeric(12,2) NOT NULL,
    fecha_aplicacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_beca_obligacion_monto CHECK ((monto_aplicado >= (0)::numeric)),
    CONSTRAINT ck_beca_obligacion_porcentaje CHECK (((porcentaje_aplicado >= (0)::numeric) AND (porcentaje_aplicado <= (100)::numeric)))
);


ALTER TABLE school.beca_obligacion OWNER TO postgres;

--
-- TOC entry 291 (class 1259 OID 33885)
-- Name: beca_obligacion_id_beca_obligacion_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.beca_obligacion_id_beca_obligacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.beca_obligacion_id_beca_obligacion_seq OWNER TO postgres;

--
-- TOC entry 5642 (class 0 OID 0)
-- Dependencies: 291
-- Name: beca_obligacion_id_beca_obligacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.beca_obligacion_id_beca_obligacion_seq OWNED BY school.beca_obligacion.id_beca_obligacion;


--
-- TOC entry 274 (class 1259 OID 27398)
-- Name: cambio_carrera; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.cambio_carrera (
    id_cambio bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    id_inscripcion_origen bigint NOT NULL,
    id_inscripcion_destino bigint,
    fecha_solicitud timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_aprobacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    motivo text,
    estado school.estado_cambio_carrera DEFAULT 'SOLICITADO'::school.estado_cambio_carrera NOT NULL,
    id_usuario bigint,
    observaciones text
);


ALTER TABLE school.cambio_carrera OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 27397)
-- Name: cambio_carrera_id_cambio_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.cambio_carrera_id_cambio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.cambio_carrera_id_cambio_seq OWNER TO postgres;

--
-- TOC entry 5643 (class 0 OID 0)
-- Dependencies: 273
-- Name: cambio_carrera_id_cambio_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.cambio_carrera_id_cambio_seq OWNED BY school.cambio_carrera.id_cambio;


--
-- TOC entry 224 (class 1259 OID 26764)
-- Name: carrera; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.carrera (
    id_carrera bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE school.carrera OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 26956)
-- Name: carrera_ciclo; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.carrera_ciclo (
    id_carrera_ciclo bigint NOT NULL,
    id_carrera bigint NOT NULL,
    id_ciclo bigint NOT NULL,
    nombre_comercial character varying(150),
    estado boolean DEFAULT true NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE school.carrera_ciclo OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 26955)
-- Name: carrera_ciclo_id_carrera_ciclo_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.carrera_ciclo_id_carrera_ciclo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.carrera_ciclo_id_carrera_ciclo_seq OWNER TO postgres;

--
-- TOC entry 5644 (class 0 OID 0)
-- Dependencies: 243
-- Name: carrera_ciclo_id_carrera_ciclo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.carrera_ciclo_id_carrera_ciclo_seq OWNED BY school.carrera_ciclo.id_carrera_ciclo;


--
-- TOC entry 223 (class 1259 OID 26763)
-- Name: carrera_id_carrera_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.carrera_id_carrera_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.carrera_id_carrera_seq OWNER TO postgres;

--
-- TOC entry 5645 (class 0 OID 0)
-- Dependencies: 223
-- Name: carrera_id_carrera_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.carrera_id_carrera_seq OWNED BY school.carrera.id_carrera;


--
-- TOC entry 226 (class 1259 OID 26788)
-- Name: ciclo_escolar; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.ciclo_escolar OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 26787)
-- Name: ciclo_escolar_id_ciclo_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.ciclo_escolar_id_ciclo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.ciclo_escolar_id_ciclo_seq OWNER TO postgres;

--
-- TOC entry 5646 (class 0 OID 0)
-- Dependencies: 225
-- Name: ciclo_escolar_id_ciclo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.ciclo_escolar_id_ciclo_seq OWNED BY school.ciclo_escolar.id_ciclo;


--
-- TOC entry 246 (class 1259 OID 26982)
-- Name: contacto; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.contacto OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 26981)
-- Name: contacto_id_contacto_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.contacto_id_contacto_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.contacto_id_contacto_seq OWNER TO postgres;

--
-- TOC entry 5647 (class 0 OID 0)
-- Dependencies: 245
-- Name: contacto_id_contacto_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.contacto_id_contacto_seq OWNED BY school.contacto.id_contacto;


--
-- TOC entry 228 (class 1259 OID 26806)
-- Name: descuento; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.descuento OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 26805)
-- Name: descuento_id_descuento_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.descuento_id_descuento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.descuento_id_descuento_seq OWNER TO postgres;

--
-- TOC entry 5648 (class 0 OID 0)
-- Dependencies: 227
-- Name: descuento_id_descuento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.descuento_id_descuento_seq OWNED BY school.descuento.id_descuento;


--
-- TOC entry 284 (class 1259 OID 27600)
-- Name: descuento_obligacion; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.descuento_obligacion (
    id_descuento_obligacion bigint NOT NULL,
    id_descuento bigint NOT NULL,
    id_obligacion bigint NOT NULL,
    monto_aplicado numeric(12,2) NOT NULL,
    fecha_aplicacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_descuento_aplicado CHECK ((monto_aplicado > (0)::numeric))
);


ALTER TABLE school.descuento_obligacion OWNER TO postgres;

--
-- TOC entry 283 (class 1259 OID 27599)
-- Name: descuento_obligacion_id_descuento_obligacion_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.descuento_obligacion_id_descuento_obligacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.descuento_obligacion_id_descuento_obligacion_seq OWNER TO postgres;

--
-- TOC entry 5649 (class 0 OID 0)
-- Dependencies: 283
-- Name: descuento_obligacion_id_descuento_obligacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.descuento_obligacion_id_descuento_obligacion_seq OWNED BY school.descuento_obligacion.id_descuento_obligacion;


--
-- TOC entry 259 (class 1259 OID 27155)
-- Name: documento_expediente; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.documento_expediente OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 27154)
-- Name: documento_expediente_id_documento_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.documento_expediente_id_documento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.documento_expediente_id_documento_seq OWNER TO postgres;

--
-- TOC entry 5650 (class 0 OID 0)
-- Dependencies: 258
-- Name: documento_expediente_id_documento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.documento_expediente_id_documento_seq OWNED BY school.documento_expediente.id_documento;


--
-- TOC entry 230 (class 1259 OID 26824)
-- Name: empleado; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.empleado OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 26823)
-- Name: empleado_id_empleado_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.empleado_id_empleado_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.empleado_id_empleado_seq OWNER TO postgres;

--
-- TOC entry 5651 (class 0 OID 0)
-- Dependencies: 229
-- Name: empleado_id_empleado_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.empleado_id_empleado_seq OWNED BY school.empleado.id_empleado;


--
-- TOC entry 232 (class 1259 OID 26848)
-- Name: estudiante; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.estudiante OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 26847)
-- Name: estudiante_id_estudiante_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.estudiante_id_estudiante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.estudiante_id_estudiante_seq OWNER TO postgres;

--
-- TOC entry 5652 (class 0 OID 0)
-- Dependencies: 231
-- Name: estudiante_id_estudiante_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.estudiante_id_estudiante_seq OWNED BY school.estudiante.id_estudiante;


--
-- TOC entry 248 (class 1259 OID 27002)
-- Name: evaluacion; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.evaluacion (
    id_evaluacion bigint NOT NULL,
    id_ciclo bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    fecha_evaluacion date NOT NULL,
    fecha_corte_finanzas date NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE school.evaluacion OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 27001)
-- Name: evaluacion_id_evaluacion_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.evaluacion_id_evaluacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.evaluacion_id_evaluacion_seq OWNER TO postgres;

--
-- TOC entry 5653 (class 0 OID 0)
-- Dependencies: 247
-- Name: evaluacion_id_evaluacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.evaluacion_id_evaluacion_seq OWNED BY school.evaluacion.id_evaluacion;


--
-- TOC entry 250 (class 1259 OID 27021)
-- Name: expediente; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.expediente (
    id_expediente bigint NOT NULL,
    id_estudiante bigint NOT NULL,
    observaciones text,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE school.expediente OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 27020)
-- Name: expediente_id_expediente_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.expediente_id_expediente_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.expediente_id_expediente_seq OWNER TO postgres;

--
-- TOC entry 5654 (class 0 OID 0)
-- Dependencies: 249
-- Name: expediente_id_expediente_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.expediente_id_expediente_seq OWNED BY school.expediente.id_expediente;


--
-- TOC entry 261 (class 1259 OID 27182)
-- Name: grado; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.grado (
    id_grado bigint NOT NULL,
    id_carrera_ciclo bigint NOT NULL,
    nombre character varying(100) NOT NULL,
    nivel_orden integer,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_grado_orden CHECK (((nivel_orden IS NULL) OR (nivel_orden > 0)))
);


ALTER TABLE school.grado OWNER TO postgres;

--
-- TOC entry 260 (class 1259 OID 27181)
-- Name: grado_id_grado_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.grado_id_grado_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.grado_id_grado_seq OWNER TO postgres;

--
-- TOC entry 5655 (class 0 OID 0)
-- Dependencies: 260
-- Name: grado_id_grado_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.grado_id_grado_seq OWNED BY school.grado.id_grado;


--
-- TOC entry 272 (class 1259 OID 27348)
-- Name: inscripcion; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.inscripcion OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 27347)
-- Name: inscripcion_id_inscripcion_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.inscripcion_id_inscripcion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.inscripcion_id_inscripcion_seq OWNER TO postgres;

--
-- TOC entry 5656 (class 0 OID 0)
-- Dependencies: 271
-- Name: inscripcion_id_inscripcion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.inscripcion_id_inscripcion_seq OWNED BY school.inscripcion.id_inscripcion;


--
-- TOC entry 276 (class 1259 OID 27444)
-- Name: movimiento_saldo; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.movimiento_saldo OWNER TO postgres;

--
-- TOC entry 275 (class 1259 OID 27443)
-- Name: movimiento_saldo_id_movimiento_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.movimiento_saldo_id_movimiento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.movimiento_saldo_id_movimiento_seq OWNER TO postgres;

--
-- TOC entry 5657 (class 0 OID 0)
-- Dependencies: 275
-- Name: movimiento_saldo_id_movimiento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.movimiento_saldo_id_movimiento_seq OWNED BY school.movimiento_saldo.id_movimiento;


--
-- TOC entry 234 (class 1259 OID 26872)
-- Name: notificacion; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.notificacion (
    id_notificacion bigint NOT NULL,
    titulo character varying(200) NOT NULL,
    mensaje text NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_usuario bigint,
    CONSTRAINT ck_notificacion_mensaje CHECK ((length(TRIM(BOTH FROM mensaje)) > 0))
);


ALTER TABLE school.notificacion OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 27202)
-- Name: notificacion_destinatario; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.notificacion_destinatario (
    id_destinatario bigint NOT NULL,
    id_notificacion bigint NOT NULL,
    id_contacto bigint NOT NULL,
    estado character varying(30) DEFAULT 'GENERADO'::character varying NOT NULL,
    fecha_generado timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_abierto timestamp without time zone
);


ALTER TABLE school.notificacion_destinatario OWNER TO postgres;

--
-- TOC entry 262 (class 1259 OID 27201)
-- Name: notificacion_destinatario_id_destinatario_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.notificacion_destinatario_id_destinatario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.notificacion_destinatario_id_destinatario_seq OWNER TO postgres;

--
-- TOC entry 5658 (class 0 OID 0)
-- Dependencies: 262
-- Name: notificacion_destinatario_id_destinatario_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.notificacion_destinatario_id_destinatario_seq OWNED BY school.notificacion_destinatario.id_destinatario;


--
-- TOC entry 233 (class 1259 OID 26871)
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.notificacion_id_notificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.notificacion_id_notificacion_seq OWNER TO postgres;

--
-- TOC entry 5659 (class 0 OID 0)
-- Dependencies: 233
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.notificacion_id_notificacion_seq OWNED BY school.notificacion.id_notificacion;


--
-- TOC entry 278 (class 1259 OID 27488)
-- Name: obligacion; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.obligacion (
    id_obligacion bigint NOT NULL,
    id_inscripcion bigint NOT NULL,
    id_precio bigint,
    concepto character varying(150) NOT NULL,
    periodo character varying(20),
    fecha_vencimiento date,
    monto_bruto numeric(12,2) NOT NULL,
    monto_descuento numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    monto_beca numeric(12,2) DEFAULT '0'::numeric NOT NULL,
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


ALTER TABLE school.obligacion OWNER TO postgres;

--
-- TOC entry 277 (class 1259 OID 27487)
-- Name: obligacion_id_obligacion_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.obligacion_id_obligacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.obligacion_id_obligacion_seq OWNER TO postgres;

--
-- TOC entry 5660 (class 0 OID 0)
-- Dependencies: 277
-- Name: obligacion_id_obligacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.obligacion_id_obligacion_seq OWNED BY school.obligacion.id_obligacion;


--
-- TOC entry 252 (class 1259 OID 27060)
-- Name: pago; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.pago OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 27059)
-- Name: pago_id_pago_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.pago_id_pago_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.pago_id_pago_seq OWNER TO postgres;

--
-- TOC entry 5661 (class 0 OID 0)
-- Dependencies: 251
-- Name: pago_id_pago_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.pago_id_pago_seq OWNED BY school.pago.id_pago;


--
-- TOC entry 236 (class 1259 OID 26887)
-- Name: permiso; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.permiso (
    id_permiso bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text
);


ALTER TABLE school.permiso OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 26886)
-- Name: permiso_id_permiso_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.permiso_id_permiso_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.permiso_id_permiso_seq OWNER TO postgres;

--
-- TOC entry 5662 (class 0 OID 0)
-- Dependencies: 235
-- Name: permiso_id_permiso_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.permiso_id_permiso_seq OWNED BY school.permiso.id_permiso;


--
-- TOC entry 265 (class 1259 OID 27234)
-- Name: precio_carrera; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.precio_carrera OWNER TO postgres;

--
-- TOC entry 264 (class 1259 OID 27233)
-- Name: precio_carrera_id_precio_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.precio_carrera_id_precio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.precio_carrera_id_precio_seq OWNER TO postgres;

--
-- TOC entry 5663 (class 0 OID 0)
-- Dependencies: 264
-- Name: precio_carrera_id_precio_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.precio_carrera_id_precio_seq OWNED BY school.precio_carrera.id_precio;


--
-- TOC entry 267 (class 1259 OID 27258)
-- Name: recibo; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.recibo (
    id_recibo bigint NOT NULL,
    id_pago bigint NOT NULL,
    numero_recibo character varying(50) NOT NULL,
    codigo_verificacion character varying(100) NOT NULL,
    fecha_emision timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE school.recibo OWNER TO postgres;

--
-- TOC entry 266 (class 1259 OID 27257)
-- Name: recibo_id_recibo_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.recibo_id_recibo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.recibo_id_recibo_seq OWNER TO postgres;

--
-- TOC entry 5664 (class 0 OID 0)
-- Dependencies: 266
-- Name: recibo_id_recibo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.recibo_id_recibo_seq OWNED BY school.recibo.id_recibo;


--
-- TOC entry 238 (class 1259 OID 26900)
-- Name: rol; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.rol (
    id_rol bigint NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE school.rol OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 26899)
-- Name: rol_id_rol_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.rol_id_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.rol_id_rol_seq OWNER TO postgres;

--
-- TOC entry 5665 (class 0 OID 0)
-- Dependencies: 237
-- Name: rol_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.rol_id_rol_seq OWNED BY school.rol.id_rol;


--
-- TOC entry 253 (class 1259 OID 27086)
-- Name: rol_permiso; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.rol_permiso (
    id_rol bigint NOT NULL,
    id_permiso bigint NOT NULL
);


ALTER TABLE school.rol_permiso OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 27282)
-- Name: saldo_favor; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.saldo_favor OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 27281)
-- Name: saldo_favor_id_saldo_favor_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.saldo_favor_id_saldo_favor_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.saldo_favor_id_saldo_favor_seq OWNER TO postgres;

--
-- TOC entry 5666 (class 0 OID 0)
-- Dependencies: 268
-- Name: saldo_favor_id_saldo_favor_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.saldo_favor_id_saldo_favor_seq OWNED BY school.saldo_favor.id_saldo_favor;


--
-- TOC entry 280 (class 1259 OID 27534)
-- Name: solvencia; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.solvencia OWNER TO postgres;

--
-- TOC entry 279 (class 1259 OID 27533)
-- Name: solvencia_id_solvencia_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.solvencia_id_solvencia_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.solvencia_id_solvencia_seq OWNER TO postgres;

--
-- TOC entry 5667 (class 0 OID 0)
-- Dependencies: 279
-- Name: solvencia_id_solvencia_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.solvencia_id_solvencia_seq OWNED BY school.solvencia.id_solvencia;


--
-- TOC entry 240 (class 1259 OID 26915)
-- Name: tipo_documento; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.tipo_documento (
    id_tipo_documento bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    obligatorio boolean DEFAULT false NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE school.tipo_documento OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 26914)
-- Name: tipo_documento_id_tipo_documento_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.tipo_documento_id_tipo_documento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.tipo_documento_id_tipo_documento_seq OWNER TO postgres;

--
-- TOC entry 5668 (class 0 OID 0)
-- Dependencies: 239
-- Name: tipo_documento_id_tipo_documento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.tipo_documento_id_tipo_documento_seq OWNED BY school.tipo_documento.id_tipo_documento;


--
-- TOC entry 255 (class 1259 OID 27112)
-- Name: usuario; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.usuario OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 27111)
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: school; Owner: postgres
--

CREATE SEQUENCE school.usuario_id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE school.usuario_id_usuario_seq OWNER TO postgres;

--
-- TOC entry 5669 (class 0 OID 0)
-- Dependencies: 254
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.usuario_id_usuario_seq OWNED BY school.usuario.id_usuario;


--
-- TOC entry 270 (class 1259 OID 27312)
-- Name: usuario_rol; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.usuario_rol (
    id_usuario bigint NOT NULL,
    id_rol bigint NOT NULL
);


ALTER TABLE school.usuario_rol OWNER TO postgres;

--
-- TOC entry 285 (class 1259 OID 27622)
-- Name: vw_saldo_obligaciones; Type: VIEW; Schema: school; Owner: postgres
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


ALTER VIEW school.vw_saldo_obligaciones OWNER TO postgres;

--
-- TOC entry 286 (class 1259 OID 27650)
-- Name: vw_estudiantes_insolventes; Type: VIEW; Schema: school; Owner: postgres
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


ALTER VIEW school.vw_estudiantes_insolventes OWNER TO postgres;

--
-- TOC entry 287 (class 1259 OID 27655)
-- Name: vw_dashboard_financiero; Type: VIEW; Schema: school; Owner: postgres
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


ALTER VIEW school.vw_dashboard_financiero OWNER TO postgres;

--
-- TOC entry 288 (class 1259 OID 27660)
-- Name: vw_deuda_por_estudiante; Type: VIEW; Schema: school; Owner: postgres
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


ALTER VIEW school.vw_deuda_por_estudiante OWNER TO postgres;

--
-- TOC entry 289 (class 1259 OID 27665)
-- Name: vw_deuda_por_grado; Type: VIEW; Schema: school; Owner: postgres
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


ALTER VIEW school.vw_deuda_por_grado OWNER TO postgres;

--
-- TOC entry 290 (class 1259 OID 27670)
-- Name: vw_estado_cuenta_estudiante; Type: VIEW; Schema: school; Owner: postgres
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


ALTER VIEW school.vw_estado_cuenta_estudiante OWNER TO postgres;

--
-- TOC entry 5195 (class 2604 OID 27576)
-- Name: aplicacion_pago id_aplicacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago ALTER COLUMN id_aplicacion SET DEFAULT nextval('school.aplicacion_pago_id_aplicacion_seq'::regclass);


--
-- TOC entry 5158 (class 2604 OID 27140)
-- Name: auditoria id_auditoria; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.auditoria ALTER COLUMN id_auditoria SET DEFAULT nextval('school.auditoria_id_auditoria_seq'::regclass);


--
-- TOC entry 5114 (class 2604 OID 26749)
-- Name: beca id_beca; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca ALTER COLUMN id_beca SET DEFAULT nextval('school.beca_id_beca_seq'::regclass);


--
-- TOC entry 5139 (class 2604 OID 26935)
-- Name: beca_estudiante id_beca_estudiante; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante ALTER COLUMN id_beca_estudiante SET DEFAULT nextval('school.beca_estudiante_id_beca_estudiante_seq'::regclass);


--
-- TOC entry 5199 (class 2604 OID 33889)
-- Name: beca_obligacion id_beca_obligacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_obligacion ALTER COLUMN id_beca_obligacion SET DEFAULT nextval('school.beca_obligacion_id_beca_obligacion_seq'::regclass);


--
-- TOC entry 5181 (class 2604 OID 27401)
-- Name: cambio_carrera id_cambio; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera ALTER COLUMN id_cambio SET DEFAULT nextval('school.cambio_carrera_id_cambio_seq'::regclass);


--
-- TOC entry 5116 (class 2604 OID 26767)
-- Name: carrera id_carrera; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera ALTER COLUMN id_carrera SET DEFAULT nextval('school.carrera_id_carrera_seq'::regclass);


--
-- TOC entry 5140 (class 2604 OID 26959)
-- Name: carrera_ciclo id_carrera_ciclo; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo ALTER COLUMN id_carrera_ciclo SET DEFAULT nextval('school.carrera_ciclo_id_carrera_ciclo_seq'::regclass);


--
-- TOC entry 5119 (class 2604 OID 26791)
-- Name: ciclo_escolar id_ciclo; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.ciclo_escolar ALTER COLUMN id_ciclo SET DEFAULT nextval('school.ciclo_escolar_id_ciclo_seq'::regclass);


--
-- TOC entry 5143 (class 2604 OID 26985)
-- Name: contacto id_contacto; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.contacto ALTER COLUMN id_contacto SET DEFAULT nextval('school.contacto_id_contacto_seq'::regclass);


--
-- TOC entry 5122 (class 2604 OID 26809)
-- Name: descuento id_descuento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento ALTER COLUMN id_descuento SET DEFAULT nextval('school.descuento_id_descuento_seq'::regclass);


--
-- TOC entry 5197 (class 2604 OID 27603)
-- Name: descuento_obligacion id_descuento_obligacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion ALTER COLUMN id_descuento_obligacion SET DEFAULT nextval('school.descuento_obligacion_id_descuento_obligacion_seq'::regclass);


--
-- TOC entry 5160 (class 2604 OID 27158)
-- Name: documento_expediente id_documento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente ALTER COLUMN id_documento SET DEFAULT nextval('school.documento_expediente_id_documento_seq'::regclass);


--
-- TOC entry 5124 (class 2604 OID 26827)
-- Name: empleado id_empleado; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.empleado ALTER COLUMN id_empleado SET DEFAULT nextval('school.empleado_id_empleado_seq'::regclass);


--
-- TOC entry 5127 (class 2604 OID 26851)
-- Name: estudiante id_estudiante; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante ALTER COLUMN id_estudiante SET DEFAULT nextval('school.estudiante_id_estudiante_seq'::regclass);


--
-- TOC entry 5146 (class 2604 OID 27005)
-- Name: evaluacion id_evaluacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.evaluacion ALTER COLUMN id_evaluacion SET DEFAULT nextval('school.evaluacion_id_evaluacion_seq'::regclass);


--
-- TOC entry 5148 (class 2604 OID 27024)
-- Name: expediente id_expediente; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente ALTER COLUMN id_expediente SET DEFAULT nextval('school.expediente_id_expediente_seq'::regclass);


--
-- TOC entry 5163 (class 2604 OID 27185)
-- Name: grado id_grado; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado ALTER COLUMN id_grado SET DEFAULT nextval('school.grado_id_grado_seq'::regclass);


--
-- TOC entry 5176 (class 2604 OID 27351)
-- Name: inscripcion id_inscripcion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion ALTER COLUMN id_inscripcion SET DEFAULT nextval('school.inscripcion_id_inscripcion_seq'::regclass);


--
-- TOC entry 5185 (class 2604 OID 27447)
-- Name: movimiento_saldo id_movimiento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo ALTER COLUMN id_movimiento SET DEFAULT nextval('school.movimiento_saldo_id_movimiento_seq'::regclass);


--
-- TOC entry 5131 (class 2604 OID 26875)
-- Name: notificacion id_notificacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion ALTER COLUMN id_notificacion SET DEFAULT nextval('school.notificacion_id_notificacion_seq'::regclass);


--
-- TOC entry 5165 (class 2604 OID 27205)
-- Name: notificacion_destinatario id_destinatario; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario ALTER COLUMN id_destinatario SET DEFAULT nextval('school.notificacion_destinatario_id_destinatario_seq'::regclass);


--
-- TOC entry 5188 (class 2604 OID 27491)
-- Name: obligacion id_obligacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion ALTER COLUMN id_obligacion SET DEFAULT nextval('school.obligacion_id_obligacion_seq'::regclass);


--
-- TOC entry 5151 (class 2604 OID 27063)
-- Name: pago id_pago; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.pago ALTER COLUMN id_pago SET DEFAULT nextval('school.pago_id_pago_seq'::regclass);


--
-- TOC entry 5133 (class 2604 OID 26890)
-- Name: permiso id_permiso; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.permiso ALTER COLUMN id_permiso SET DEFAULT nextval('school.permiso_id_permiso_seq'::regclass);


--
-- TOC entry 5168 (class 2604 OID 27237)
-- Name: precio_carrera id_precio; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.precio_carrera ALTER COLUMN id_precio SET DEFAULT nextval('school.precio_carrera_id_precio_seq'::regclass);


--
-- TOC entry 5171 (class 2604 OID 27261)
-- Name: recibo id_recibo; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo ALTER COLUMN id_recibo SET DEFAULT nextval('school.recibo_id_recibo_seq'::regclass);


--
-- TOC entry 5134 (class 2604 OID 26903)
-- Name: rol id_rol; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol ALTER COLUMN id_rol SET DEFAULT nextval('school.rol_id_rol_seq'::regclass);


--
-- TOC entry 5173 (class 2604 OID 27285)
-- Name: saldo_favor id_saldo_favor; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.saldo_favor ALTER COLUMN id_saldo_favor SET DEFAULT nextval('school.saldo_favor_id_saldo_favor_seq'::regclass);


--
-- TOC entry 5193 (class 2604 OID 27537)
-- Name: solvencia id_solvencia; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia ALTER COLUMN id_solvencia SET DEFAULT nextval('school.solvencia_id_solvencia_seq'::regclass);


--
-- TOC entry 5136 (class 2604 OID 26918)
-- Name: tipo_documento id_tipo_documento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.tipo_documento ALTER COLUMN id_tipo_documento SET DEFAULT nextval('school.tipo_documento_id_tipo_documento_seq'::regclass);


--
-- TOC entry 5155 (class 2604 OID 27115)
-- Name: usuario id_usuario; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('school.usuario_id_usuario_seq'::regclass);


--
-- TOC entry 5566 (class 0 OID 26730)
-- Dependencies: 220
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.alembic_version (version_num) FROM stdin;
5d15b947d4ca
\.


--
-- TOC entry 5628 (class 0 OID 27573)
-- Dependencies: 282
-- Data for Name: aplicacion_pago; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.aplicacion_pago (id_aplicacion, id_pago, id_obligacion, monto_aplicado, fecha_aplicacion) FROM stdin;
13	7	14	500.00	2026-09-19 00:07:09.926554
14	8	13	500.00	2026-09-19 00:10:25.414076
15	8	14	250.00	2026-09-19 00:10:25.414076
16	8	15	750.00	2026-09-19 00:10:25.414076
17	8	16	750.00	2026-09-19 00:10:25.414076
18	8	17	750.00	2026-09-19 00:10:25.414076
19	8	18	750.00	2026-09-19 00:10:25.414076
20	8	19	750.00	2026-09-19 00:10:25.414076
21	8	20	500.00	2026-09-19 00:10:25.414076
28	14	30	100.00	2026-09-26 00:03:35.115784
29	15	31	30.00	2026-09-26 00:03:35.400613
\.


--
-- TOC entry 5603 (class 0 OID 27137)
-- Dependencies: 257
-- Data for Name: auditoria; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.auditoria (id_auditoria, id_usuario, fecha_evento, modulo, accion, tabla_afectada, id_registro, descripcion, datos_anteriores, datos_nuevos, ip) FROM stdin;
1	1	2026-09-25 22:02:21.511535	FINANZAS	REGISTRAR_PAGO	pago	13	Registro de pago	\N	{"estado": "CONFIRMADO", "metodo": "EFECTIVO", "id_pago": 13, "creado_en": "2026-09-25T22:02:21.511535", "fecha_pago": "2026-09-25T22:02:21.511535", "id_usuario": 1, "referencia": "Pago auditoria", "monto_total": 1.0, "id_estudiante": 5, "observaciones": "Test de auditoria", "total_aplicado": 0, "saldo_disponible": 1.0}	\N
2	1	2026-09-25 22:15:20.95577	NOTIFICACIONES	CREAR_NOTIFICACION	notificacion	5	Creación de notificación	\N	{"titulo": "Test Auditoria", "mensaje": "Test de registros de auditorias", "id_usuario": 1, "destinatarios": [{"email": "maria@example.com", "estado": "GENERADO", "contacto": "María Pérez", "telefono": "55550000", "whatsapp": "55550000", "estudiante": "William Montoya", "id_contacto": 1, "es_principal": false, "fecha_abierto": null, "id_estudiante": 5, "fecha_generado": "2026-09-25T22:15:20.955770", "id_destinatario": 6, "codigo_estudiante": "EST-0001"}], "fecha_creacion": "2026-09-25T22:15:20.955770", "total_abiertos": 0, "id_notificacion": 5, "total_pendientes": 1, "total_destinatarios": 1}	\N
3	1	2026-09-26 00:03:33.984669	SEGURIDAD	CREAR_ROL	rol	2	Creación del rol E2E_VIEWER_20260926000333_D8C5ED	\N	{"activo": true, "id_rol": 2, "nombre": "E2E_VIEWER_20260926000333_D8C5ED", "permisos": [], "descripcion": "Rol temporal de prueba E2E"}	\N
4	1	2026-09-26 00:03:34.03661	SEGURIDAD	REEMPLAZAR_PERMISOS_ROL	rol_permiso	2	Reemplazo de permisos del rol E2E_VIEWER_20260926000333_D8C5ED	{"activo": true, "id_rol": 2, "nombre": "E2E_VIEWER_20260926000333_D8C5ED", "permisos": [], "descripcion": "Rol temporal de prueba E2E"}	{"activo": true, "id_rol": 2, "nombre": "E2E_VIEWER_20260926000333_D8C5ED", "permisos": [{"nombre": "ESTUDIANTES_VER", "id_permiso": 5, "descripcion": "Consultar información de estudiantes"}], "descripcion": "Rol temporal de prueba E2E"}	\N
5	1	2026-09-26 00:03:34.100833	SEGURIDAD	CREAR_USUARIO	usuario	2	Creación del usuario e2e_viewer_20260926000333_d8c5ed	\N	{"cargo": "Prueba E2E", "roles": [{"activo": true, "id_rol": 2, "nombre": "E2E_VIEWER_20260926000333_D8C5ED", "descripcion": "Rol temporal de prueba E2E"}], "estado": "ACTIVO", "empleado": "E2E Viewer 20260926000333_d8c5ed", "permisos": [{"nombre": "ESTUDIANTES_VER", "id_permiso": 5, "descripcion": "Consultar información de estudiantes"}], "username": "e2e_viewer_20260926000333_d8c5ed", "creado_en": "2026-09-26T00:03:34.100833", "id_usuario": 2, "id_empleado": 3, "ultimo_acceso": null}	\N
6	1	2026-09-26 00:03:34.71752	ACADEMICO	CREAR_INSCRIPCION	inscripcion	14	Creación de inscripción para estudiante 8	\N	{"tipo": "NUEVA", "ciclo": "E2E Ciclo 20260926000333_d8c5ed", "grado": "E2E Grado 20260926000333_d8c5ed", "estado": "ACTIVA", "carrera": "E2E Carrera 20260926000333_d8c5ed", "id_grado": 8, "creado_en": "2026-09-26T00:03:34.717520", "estudiante": "Estudiante E2E 20260926000333_d8c5ed", "id_estudiante": 8, "observaciones": "Inscripción E2E", "id_inscripcion": 14, "id_carrera_ciclo": 8, "codigo_estudiante": "E2E-20260926000333_d8c5ed", "fecha_inscripcion": "2026-09-26"}	\N
7	1	2026-09-26 00:03:34.894101	FINANZAS	CREAR_OBLIGACION_DESDE_PRECIO	obligacion	30	Creación de obligación desde precio 9	\N	{"saldo": 100.0, "estado": "PENDIENTE", "periodo": null, "concepto": "Inscripción E2E 20260926000333_d8c5ed", "creado_en": "2026-09-26T00:03:34.894101", "id_precio": 9, "monto_beca": 0.0, "monto_neto": 100.0, "monto_bruto": 100.0, "total_pagado": 0, "id_obligacion": 30, "id_inscripcion": 14, "monto_descuento": 0.0, "tipo_obligacion": "INSCRIPCION", "fecha_vencimiento": "2026-09-26"}	\N
8	1	2026-09-26 00:03:35.066792	FINANZAS	REGISTRAR_PAGO	pago	14	Registro de pago	\N	{"estado": "CONFIRMADO", "metodo": "EFECTIVO", "id_pago": 14, "creado_en": "2026-09-26T00:03:35.066792", "fecha_pago": "2026-09-26T00:03:35.066792", "id_usuario": 1, "referencia": "E2E-20260926000333_d8c5ed", "monto_total": 100.0, "id_estudiante": 8, "observaciones": "Pago manual E2E", "total_aplicado": 0, "saldo_disponible": 100.0}	\N
9	1	2026-09-26 00:03:35.115784	FINANZAS	APLICAR_PAGO	aplicacion_pago	28	Aplicación del pago 14 a la obligación 30	{"pago": {"estado": "CONFIRMADO", "metodo": "EFECTIVO", "id_pago": 14, "creado_en": "2026-09-26T00:03:35.066792", "fecha_pago": "2026-09-26T00:03:35.066792", "id_usuario": 1, "referencia": "E2E-20260926000333_d8c5ed", "monto_total": 100.0, "id_estudiante": 8, "observaciones": "Pago manual E2E", "total_aplicado": 0, "saldo_disponible": 100.0}}	{"pago": {"estado": "CONFIRMADO", "metodo": "EFECTIVO", "id_pago": 14, "creado_en": "2026-09-26T00:03:35.066792", "fecha_pago": "2026-09-26T00:03:35.066792", "id_usuario": 1, "referencia": "E2E-20260926000333_d8c5ed", "monto_total": 100.0, "id_estudiante": 8, "observaciones": "Pago manual E2E", "total_aplicado": 100.0, "saldo_disponible": 0.0}, "aplicacion": {"id_pago": 14, "periodo": null, "concepto": "Inscripción E2E 20260926000333_d8c5ed", "id_aplicacion": 28, "id_obligacion": 30, "monto_aplicado": 100.0, "fecha_aplicacion": "2026-09-26T00:03:35.115784"}}	\N
10	1	2026-09-26 00:03:35.23361	FINANZAS	GENERAR_RECIBO	recibo	37	Generación de recibo para el pago 14	\N	{"pago": {"estado": "CONFIRMADO", "metodo": "EFECTIVO", "id_pago": 14, "creado_en": "2026-09-26T00:03:35.066792", "fecha_pago": "2026-09-26T00:03:35.066792", "id_usuario": 1, "referencia": "E2E-20260926000333_d8c5ed", "monto_total": 100.0, "id_estudiante": 8, "observaciones": "Pago manual E2E", "total_aplicado": 100.0, "saldo_disponible": 0.0}, "recibo": {"id_pago": 14, "id_recibo": 37, "fecha_emision": "2026-09-26T00:03:35.233610", "numero_recibo": "REC-2026-00000014", "codigo_verificacion": "VER-93d4f388b9c1b90e320eb02010693158"}}	\N
11	1	2026-09-26 00:03:35.308234	FINANZAS	REGISTRAR_PAGO_AUTOMATICO	pago	15	Registro de pago automático	\N	{"pago": {"estado": "CONFIRMADO", "metodo": "EFECTIVO", "id_pago": 15, "creado_en": "2026-09-26T00:03:35.308234", "fecha_pago": "2026-09-26T00:03:35.308234", "id_usuario": 1, "referencia": "E2E-AUTO-20260926000333_d8c5ed", "monto_total": 30.0, "id_estudiante": 8, "observaciones": "Pago automático E2E", "total_aplicado": 0, "saldo_disponible": 30.0}, "saldo_favor": {"estado": "ACTIVO", "id_estudiante": 8, "observaciones": "Saldo generado automáticamente", "id_pago_origen": 15, "id_saldo_favor": 4, "monto_original": 30.0, "fecha_generacion": "2026-09-26T00:03:35.308234", "monto_disponible": 30.0}}	\N
12	1	2026-09-26 00:03:35.347055	FINANZAS	CREAR_OBLIGACION_MANUAL	obligacion	31	Creación manual de obligación para inscripción 14	\N	{"saldo": 30.0, "estado": "PENDIENTE", "periodo": "2026", "concepto": "Constancia E2E 20260926000333_d8c5ed", "creado_en": "2026-09-26T00:03:35.347055", "id_precio": null, "monto_beca": 0.0, "monto_neto": 30.0, "monto_bruto": 30.0, "total_pagado": 0, "id_obligacion": 31, "id_inscripcion": 14, "monto_descuento": 0.0, "tipo_obligacion": "CONSTANCIA", "fecha_vencimiento": "2026-09-26"}	\N
13	1	2026-09-26 00:03:35.400613	FINANZAS	APLICAR_SALDO_FAVOR	saldo_favor	4	Aplicación de saldo a favor a la obligación 31	{"estado": "ACTIVO", "id_estudiante": 8, "observaciones": "Saldo generado automáticamente", "id_pago_origen": 15, "id_saldo_favor": 4, "monto_original": 30.0, "fecha_generacion": "2026-09-26T00:03:35.308234", "monto_disponible": 30.0}	{"saldo_favor": {"estado": "AGOTADO", "id_estudiante": 8, "observaciones": "Saldo generado automáticamente", "id_pago_origen": 15, "id_saldo_favor": 4, "monto_original": 30.0, "fecha_generacion": "2026-09-26T00:03:35.308234", "monto_disponible": 0.0}, "id_obligacion": 31, "monto_aplicado": 30.0}	\N
14	1	2026-09-26 00:03:35.564567	FINANZAS	GENERAR_SOLVENCIA	solvencia	5	Generación de solvencia para estudiante 8	\N	{"ciclo": "E2E Ciclo 20260926000333_d8c5ed", "grado": "E2E Grado 20260926000333_d8c5ed", "estado": "SOLVENTE", "carrera": "E2E Carrera 20260926000333_d8c5ed", "estudiante": "Estudiante E2E 20260926000333_d8c5ed", "evaluacion": "E2E Evaluación 20260926000333_d8c5ed", "fecha_corte": "2026-09-26", "saldo_corte": 0.0, "id_solvencia": 5, "id_estudiante": 8, "id_evaluacion": 5, "observaciones": null, "id_inscripcion": 14, "fecha_generacion": "2026-09-26T00:03:35.564567", "codigo_estudiante": "E2E-20260926000333_d8c5ed", "codigo_verificacion": "SOL-20260926000335-90012"}	\N
15	1	2026-09-26 00:03:36.136867	SEGURIDAD	CAMBIAR_ESTADO_USUARIO	usuario	2	Cambio de estado del usuario e2e_viewer_20260926000333_d8c5ed	{"cargo": "Prueba E2E", "roles": [{"activo": true, "id_rol": 2, "nombre": "E2E_VIEWER_20260926000333_D8C5ED", "descripcion": "Rol temporal de prueba E2E"}], "estado": "ACTIVO", "empleado": "E2E Viewer 20260926000333_d8c5ed", "permisos": [{"nombre": "ESTUDIANTES_VER", "id_permiso": 5, "descripcion": "Consultar información de estudiantes"}], "username": "e2e_viewer_20260926000333_d8c5ed", "creado_en": "2026-09-26T00:03:34.100833", "id_usuario": 2, "id_empleado": 3, "ultimo_acceso": "2026-09-26T00:03:34.276591"}	{"cargo": "Prueba E2E", "roles": [{"activo": true, "id_rol": 2, "nombre": "E2E_VIEWER_20260926000333_D8C5ED", "descripcion": "Rol temporal de prueba E2E"}], "estado": "INACTIVO", "empleado": "E2E Viewer 20260926000333_d8c5ed", "permisos": [{"nombre": "ESTUDIANTES_VER", "id_permiso": 5, "descripcion": "Consultar información de estudiantes"}], "username": "e2e_viewer_20260926000333_d8c5ed", "creado_en": "2026-09-26T00:03:34.100833", "id_usuario": 2, "id_empleado": 3, "ultimo_acceso": "2026-09-26T00:03:34.276591"}	\N
\.


--
-- TOC entry 5568 (class 0 OID 26746)
-- Dependencies: 222
-- Data for Name: beca; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.beca (id_beca, nombre, descripcion, porcentaje, convenio, estado, fecha_inicio, fecha_fin) FROM stdin;
1	Beca Académica 50%	Beca por rendimiento académico	50.00	Convenio institucional	ACTIVA	2027-01-01	2027-10-31
\.


--
-- TOC entry 5588 (class 0 OID 26932)
-- Dependencies: 242
-- Data for Name: beca_estudiante; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.beca_estudiante (id_beca_estudiante, id_beca, id_estudiante, fecha_inicio, fecha_fin, porcentaje_aplicado, observaciones) FROM stdin;
1	1	5	2027-01-01	2027-10-31	\N	Beca ciclo 2027
\.


--
-- TOC entry 5632 (class 0 OID 33886)
-- Dependencies: 292
-- Data for Name: beca_obligacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.beca_obligacion (id_beca_obligacion, id_beca_estudiante, id_obligacion, porcentaje_aplicado, monto_aplicado, fecha_aplicacion) FROM stdin;
\.


--
-- TOC entry 5620 (class 0 OID 27398)
-- Dependencies: 274
-- Data for Name: cambio_carrera; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.cambio_carrera (id_cambio, id_estudiante, id_inscripcion_origen, id_inscripcion_destino, fecha_solicitud, fecha_aprobacion, motivo, estado, id_usuario, observaciones) FROM stdin;
\.


--
-- TOC entry 5570 (class 0 OID 26764)
-- Dependencies: 224
-- Data for Name: carrera; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.carrera (id_carrera, nombre, descripcion, activo, creado_en) FROM stdin;
5	Bachillerato en Ciencias y Letras	Bachillerato	t	2026-09-18 21:47:30.395038
8	E2E Carrera 20260926000333_d8c5ed	Carrera generada por E2E	t	2026-09-26 00:03:34.565547
\.


--
-- TOC entry 5590 (class 0 OID 26956)
-- Dependencies: 244
-- Data for Name: carrera_ciclo; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.carrera_ciclo (id_carrera_ciclo, id_carrera, id_ciclo, nombre_comercial, estado, creado_en) FROM stdin;
5	5	3	Bachillerato 2027	t	2026-09-18 21:52:01.509627
8	8	5	E2E Programa 20260926000333_d8c5ed	t	2026-09-26 00:03:34.596731
\.


--
-- TOC entry 5572 (class 0 OID 26788)
-- Dependencies: 226
-- Data for Name: ciclo_escolar; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.ciclo_escolar (id_ciclo, nombre, fecha_inicio, fecha_fin, estado, creado_en) FROM stdin;
3	Ciclo 2027	2027-01-15	2027-10-31	PLANIFICADO	2026-09-18 21:47:03.991042
5	E2E Ciclo 20260926000333_d8c5ed	2026-01-01	2026-12-31	PLANIFICADO	2026-09-26 00:03:34.50245
\.


--
-- TOC entry 5592 (class 0 OID 26982)
-- Dependencies: 246
-- Data for Name: contacto; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.contacto (id_contacto, id_estudiante, nombre, parentesco, telefono, whatsapp, email, es_principal, activo) FROM stdin;
1	5	María Pérez	Madre	55550000	55550000	maria@example.com	f	t
2	5	Carlos Pérez	Padre	55551111	55551111	carlos@example.com	t	t
\.


--
-- TOC entry 5574 (class 0 OID 26806)
-- Dependencies: 228
-- Data for Name: descuento; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.descuento (id_descuento, nombre, descripcion, porcentaje, monto_fijo, activo) FROM stdin;
\.


--
-- TOC entry 5630 (class 0 OID 27600)
-- Dependencies: 284
-- Data for Name: descuento_obligacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.descuento_obligacion (id_descuento_obligacion, id_descuento, id_obligacion, monto_aplicado, fecha_aplicacion) FROM stdin;
\.


--
-- TOC entry 5605 (class 0 OID 27155)
-- Dependencies: 259
-- Data for Name: documento_expediente; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.documento_expediente (id_documento, id_expediente, id_tipo_documento, nombre_archivo, ruta_archivo, fecha_entrega, entregado, observaciones, creado_en) FROM stdin;
1	1	1	Recibos_de_Pago_Colegio.pdf	expedientes/1/2ee62c54a7624e789cb9b01ae0f77fc8.pdf	2026-09-22	t	\N	2026-09-22 21:10:31.828898
\.


--
-- TOC entry 5576 (class 0 OID 26824)
-- Dependencies: 230
-- Data for Name: empleado; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.empleado (id_empleado, nombres, apellidos, telefono, email, cargo, activo, creado_en) FROM stdin;
2	Administrador	PaymentSchool	55550000	admin@paymentschool.local	Administrador del sistema	t	2026-09-22 22:29:49.60345
1	Administrador	PaymentSchool	55550000	admin@paymentschool.local	Administrador del sistema	t	2026-09-22 22:29:48.138265
3	E2E	Viewer 20260926000333_d8c5ed	\N	\N	Prueba E2E	t	2026-09-26 00:03:34.06688
\.


--
-- TOC entry 5578 (class 0 OID 26848)
-- Dependencies: 232
-- Data for Name: estudiante; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.estudiante (id_estudiante, codigo_estudiante, cui, nombres, apellidos, fecha_nacimiento, telefono, whatsapp, email, direccion, estado, creado_en, actualizado_en) FROM stdin;
5	EST-0001	1234567890101	William	Montoya	2010-05-15	55550000	55550000	prueba@example.com	Guatemala	ACTIVO	2026-09-16 23:41:07.440134	2026-09-16 23:48:18.965432
8	E2E-20260926000333_d8c5ed	\N	Estudiante	E2E 20260926000333_d8c5ed	\N	\N	\N	\N	\N	ACTIVO	2026-09-26 00:03:34.677825	2026-09-26 00:03:34.677825
\.


--
-- TOC entry 5594 (class 0 OID 27002)
-- Dependencies: 248
-- Data for Name: evaluacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.evaluacion (id_evaluacion, id_ciclo, nombre, fecha_evaluacion, fecha_corte_finanzas, activo) FROM stdin;
4	3	Primera Evaluación 2027	2027-04-15	2027-04-10	t
5	5	E2E Evaluación 20260926000333_d8c5ed	2026-09-26	2026-09-26	t
\.


--
-- TOC entry 5596 (class 0 OID 27021)
-- Dependencies: 250
-- Data for Name: expediente; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.expediente (id_expediente, id_estudiante, observaciones, creado_en, actualizado_en) FROM stdin;
1	5	Expediente de nuevo ingreso	2026-09-21 23:29:09.98418	2026-09-21 23:29:09.98418
\.


--
-- TOC entry 5607 (class 0 OID 27182)
-- Dependencies: 261
-- Data for Name: grado; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.grado (id_grado, id_carrera_ciclo, nombre, nivel_orden, activo) FROM stdin;
5	5	Cuarto Bachillerato	1	t
8	8	E2E Grado 20260926000333_d8c5ed	1	t
\.


--
-- TOC entry 5618 (class 0 OID 27348)
-- Dependencies: 272
-- Data for Name: inscripcion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.inscripcion (id_inscripcion, id_estudiante, id_carrera_ciclo, id_grado, fecha_inscripcion, tipo, estado, observaciones, creado_en) FROM stdin;
9	5	5	5	2026-09-18	NUEVA	ACTIVA	Inscripción inicial	2026-09-18 21:54:48.762658
14	8	8	8	2026-09-26	NUEVA	ACTIVA	Inscripción E2E	2026-09-26 00:03:34.71752
\.


--
-- TOC entry 5622 (class 0 OID 27444)
-- Dependencies: 276
-- Data for Name: movimiento_saldo; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.movimiento_saldo (id_movimiento, id_estudiante, id_inscripcion_origen, id_inscripcion_destino, tipo, monto, fecha_movimiento, motivo, estado, id_usuario, referencia) FROM stdin;
\.


--
-- TOC entry 5580 (class 0 OID 26872)
-- Dependencies: 234
-- Data for Name: notificacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.notificacion (id_notificacion, titulo, mensaje, fecha_creacion, id_usuario) FROM stdin;
1	Reunion de Padres	Se informa que la reunión sera la siguiente semana	2026-09-22 21:53:19.036678	\N
2	Aviso de saldo pendiente	Estimado/a María Pérez, se informa que el estudiante William Montoya (EST-0001) presenta un saldo pendiente de Q2250.00. Por favor, comuníquese con administración para revisar su estado de cuenta.	2026-09-22 21:56:37.487194	\N
3	Prueba Trazabilidad	Notificación generada por usuario autenticado	2026-09-25 17:19:20.05691	1
4	Aviso de saldo pendiente	Estimado/a María Pérez, se informa que el estudiante William Montoya (EST-0001) presenta un saldo pendiente de Q2250.00. Por favor, comuníquese con administración para revisar su estado de cuenta.	2026-09-25 17:19:47.997617	1
5	Test Auditoria	Test de registros de auditorias	2026-09-25 22:15:20.95577	1
\.


--
-- TOC entry 5609 (class 0 OID 27202)
-- Dependencies: 263
-- Data for Name: notificacion_destinatario; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.notificacion_destinatario (id_destinatario, id_notificacion, id_contacto, estado, fecha_generado, fecha_abierto) FROM stdin;
2	1	2	GENERADO	2026-09-22 21:53:19.036678	\N
1	1	1	ABIERTO	2026-09-22 21:53:19.036678	2026-09-22 21:53:50.860271
3	2	1	GENERADO	2026-09-22 21:56:37.487194	\N
4	3	1	GENERADO	2026-09-25 17:19:20.05691	\N
5	4	1	GENERADO	2026-09-25 17:19:47.997617	\N
6	5	1	GENERADO	2026-09-25 22:15:20.95577	\N
\.


--
-- TOC entry 5624 (class 0 OID 27488)
-- Dependencies: 278
-- Data for Name: obligacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.obligacion (id_obligacion, id_inscripcion, id_precio, concepto, periodo, fecha_vencimiento, monto_bruto, monto_descuento, monto_beca, monto_neto, estado, creado_en, tipo_obligacion) FROM stdin;
21	9	6	Mensualidad	2027-09	2027-09-05	750.00	0.00	0.00	750.00	PENDIENTE	2026-09-18 22:55:08.011915	MENSUALIDAD
22	9	6	Mensualidad	2027-10	2027-10-05	750.00	0.00	0.00	750.00	PENDIENTE	2026-09-18 22:55:08.011915	MENSUALIDAD
13	9	5	Inscripción 2027	\N	2027-01-31	500.00	0.00	0.00	500.00	PAGADA	2026-09-18 22:51:31.226555	INSCRIPCION
15	9	6	Mensualidad	2027-03	2027-03-05	750.00	0.00	0.00	750.00	PAGADA	2026-09-18 22:55:08.011915	MENSUALIDAD
16	9	6	Mensualidad	2027-04	2027-04-05	750.00	0.00	0.00	750.00	PAGADA	2026-09-18 22:55:08.011915	MENSUALIDAD
17	9	6	Mensualidad	2027-05	2027-05-05	750.00	0.00	0.00	750.00	PAGADA	2026-09-18 22:55:08.011915	MENSUALIDAD
18	9	6	Mensualidad	2027-06	2027-06-05	750.00	0.00	0.00	750.00	PAGADA	2026-09-18 22:55:08.011915	MENSUALIDAD
19	9	6	Mensualidad	2027-07	2027-07-05	750.00	0.00	0.00	750.00	PAGADA	2026-09-18 22:55:08.011915	MENSUALIDAD
20	9	6	Mensualidad	2027-08	2027-08-05	750.00	0.00	0.00	750.00	PARCIAL	2026-09-18 22:55:08.011915	MENSUALIDAD
14	9	6	Mensualidad	2027-02	2027-02-05	750.00	0.00	0.00	750.00	PARCIAL	2026-09-18 22:55:08.011915	MENSUALIDAD
30	14	9	Inscripción E2E 20260926000333_d8c5ed	\N	2026-09-26	100.00	0.00	0.00	100.00	PAGADA	2026-09-26 00:03:34.894101	INSCRIPCION
31	14	\N	Constancia E2E 20260926000333_d8c5ed	2026	2026-09-26	30.00	0.00	0.00	30.00	PAGADA	2026-09-26 00:03:35.347055	CONSTANCIA
\.


--
-- TOC entry 5598 (class 0 OID 27060)
-- Dependencies: 252
-- Data for Name: pago; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.pago (id_pago, id_estudiante, id_usuario, fecha_pago, monto_total, metodo, referencia, observaciones, estado, creado_en) FROM stdin;
8	5	\N	2026-09-19 00:10:25.414076	5000.00	TRANSFERENCIA	TRX-2026-0001	Pago automático	CONFIRMADO	2026-09-19 00:10:25.414076
7	5	\N	2026-09-19 00:04:18.568627	500.00	EFECTIVO	CAJA-0001	Abono mensualidad | ANULADO: Pago registrado por erro	ANULADO	2026-09-19 00:04:18.568627
12	5	1	2026-09-25 16:37:48.227845	200.00	EFECTIVO	TEST-TRAZABILIDAD	Prueba de usuario autenticado | ANULADO: Prueba de trazabilidad del usuario	ANULADO	2026-09-25 16:37:48.227845
13	5	1	2026-09-25 22:02:21.511535	1.00	EFECTIVO	Pago auditoria	Test de auditoria	CONFIRMADO	2026-09-25 22:02:21.511535
14	8	1	2026-09-26 00:03:35.066792	100.00	EFECTIVO	E2E-20260926000333_d8c5ed	Pago manual E2E	CONFIRMADO	2026-09-26 00:03:35.066792
15	8	1	2026-09-26 00:03:35.308234	30.00	EFECTIVO	E2E-AUTO-20260926000333_d8c5ed	Pago automático E2E	CONFIRMADO	2026-09-26 00:03:35.308234
\.


--
-- TOC entry 5582 (class 0 OID 26887)
-- Dependencies: 236
-- Data for Name: permiso; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.permiso (id_permiso, nombre, descripcion) FROM stdin;
1	REPORTES_VER	Consultar dashboard y reportes
2	PAGOS_ANULAR	Anular pagos
3	SEGURIDAD_GESTIONAR	Administrar usuarios, roles y permisos
4	SEGURIDAD_VER	Consultar empleados, usuarios, roles y permisos
5	ESTUDIANTES_VER	Consultar información de estudiantes
6	ESTUDIANTES_GESTIONAR	Crear y modificar información de estudiantes
7	EXPEDIENTES_VER	Consultar expedientes, contactos y documentos de estudiantes
8	EXPEDIENTES_GESTIONAR	Administrar expedientes, contactos y documentos de estudiantes
9	ACADEMICO_VER	Consultar información académica
10	ACADEMICO_GESTIONAR	Administrar ciclos, carreras, grados, inscripciones, evaluaciones y cambios de carrera
11	FINANZAS_VER	Todas las consultas financieras GET
12	PRECIOS_GESTIONAR	Crear, modificar y activar precios
13	OBLIGACIONES_GESTIONAR	Crear obligaciones, crear desde precio y generar mensualidades
14	PAGOS_REGISTRAR	Registrar pago, pago automático, aplicar pago, aplicar saldo a favor y generar recibo
15	BECAS_GESTIONAR	Becas, asignaciones y aplicación a obligación
16	DESCUENTOS_GESTIONAR	Descuentos y aplicación a obligación
17	SALDOS_GESTIONAR	Traslados / movimientos de saldo
18	SOLVENCIAS_GENERAR	Generar solvencias
19	NOTIFICACIONES_VER	Ver las Notificaciones
20	NOTIFICACIONES_GESTIONAR	Gestiona las notificaciones
21	AUDITORIA_VER	Consultar registros de auditoría
\.


--
-- TOC entry 5611 (class 0 OID 27234)
-- Dependencies: 265
-- Data for Name: precio_carrera; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.precio_carrera (id_precio, id_carrera_ciclo, tipo, concepto, monto, fecha_inicio, fecha_fin, activo, creado_en) FROM stdin;
5	5	INSCRIPCION	Inscripción 2027	500.00	2027-01-01	2027-03-31	t	2026-09-18 22:43:53.167377
6	5	MENSUALIDAD	Mensualidad 2027	750.00	2027-01-01	2027-10-31	t	2026-09-18 22:49:06.227528
9	8	INSCRIPCION	Inscripción E2E 20260926000333_d8c5ed	100.00	2026-01-01	2026-12-31	t	2026-09-26 00:03:34.781327
\.


--
-- TOC entry 5613 (class 0 OID 27258)
-- Dependencies: 267
-- Data for Name: recibo; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.recibo (id_recibo, id_pago, numero_recibo, codigo_verificacion, fecha_emision) FROM stdin;
3	8	REC-2026-00000008	VER-b2a834528ea29d9e5100de2f51f1df25	2026-09-19 00:16:42.151098
37	14	REC-2026-00000014	VER-93d4f388b9c1b90e320eb02010693158	2026-09-26 00:03:35.23361
\.


--
-- TOC entry 5584 (class 0 OID 26900)
-- Dependencies: 238
-- Data for Name: rol; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.rol (id_rol, nombre, descripcion, activo) FROM stdin;
1	ADMINISTRADOR	Administrador del sistema	t
2	E2E_VIEWER_20260926000333_D8C5ED	Rol temporal de prueba E2E	t
\.


--
-- TOC entry 5599 (class 0 OID 27086)
-- Dependencies: 253
-- Data for Name: rol_permiso; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.rol_permiso (id_rol, id_permiso) FROM stdin;
1	1
1	2
1	3
1	4
1	5
1	6
1	7
1	8
1	9
1	10
1	11
1	12
1	13
1	14
1	15
1	16
1	17
1	18
1	19
1	20
1	21
2	5
\.


--
-- TOC entry 5615 (class 0 OID 27282)
-- Dependencies: 269
-- Data for Name: saldo_favor; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.saldo_favor (id_saldo_favor, id_estudiante, id_pago_origen, monto_original, monto_disponible, fecha_generacion, estado, observaciones) FROM stdin;
4	8	15	30.00	0.00	2026-09-26 00:03:35.308234	AGOTADO	Saldo generado automáticamente
\.


--
-- TOC entry 5626 (class 0 OID 27534)
-- Dependencies: 280
-- Data for Name: solvencia; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.solvencia (id_solvencia, id_estudiante, id_inscripcion, id_evaluacion, fecha_generacion, fecha_corte, saldo_corte, estado, codigo_verificacion, observaciones) FROM stdin;
4	5	9	4	2026-09-21 22:53:46.616488	2027-04-10	500.00	INSOLVENTE	SOL-20260921225346-44038	\N
5	8	14	5	2026-09-26 00:03:35.564567	2026-09-26	0.00	SOLVENTE	SOL-20260926000335-90012	\N
\.


--
-- TOC entry 5586 (class 0 OID 26915)
-- Dependencies: 240
-- Data for Name: tipo_documento; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.tipo_documento (id_tipo_documento, nombre, descripcion, obligatorio, activo) FROM stdin;
1	Certificado de nacimiento	Certificación oficial de nacimiento	t	t
2	Carta de recomendación	\N	f	t
3	Fotografía	Fotografía reciente	t	t
4	string	string	f	t
\.


--
-- TOC entry 5601 (class 0 OID 27112)
-- Dependencies: 255
-- Data for Name: usuario; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.usuario (id_usuario, id_empleado, username, password_hash, estado, ultimo_acceso, creado_en) FROM stdin;
2	3	e2e_viewer_20260926000333_d8c5ed	$argon2id$v=19$m=65536,t=3,p=4$dVwXLxqH+7w5cKWvUvWS2Q$v/Qeu17Dvs+ZYOjtza0i97px30UEkwsg7EAxZo81YBQ	INACTIVO	2026-09-26 00:03:34.276591	2026-09-26 00:03:34.100833
1	1	admin	$argon2id$v=19$m=65536,t=3,p=4$l3eGbRCdCmnyCjlq4gDrYQ$q97n9rSe0RyGgUilIQQRkWseXRO/tB/C8tnDLY8n5J0	ACTIVO	2026-09-28 23:53:40.676837	2026-09-22 22:30:34.480504
\.


--
-- TOC entry 5616 (class 0 OID 27312)
-- Dependencies: 270
-- Data for Name: usuario_rol; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.usuario_rol (id_usuario, id_rol) FROM stdin;
1	1
2	2
\.


--
-- TOC entry 5670 (class 0 OID 0)
-- Dependencies: 281
-- Name: aplicacion_pago_id_aplicacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.aplicacion_pago_id_aplicacion_seq', 29, true);


--
-- TOC entry 5671 (class 0 OID 0)
-- Dependencies: 256
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.auditoria_id_auditoria_seq', 15, true);


--
-- TOC entry 5672 (class 0 OID 0)
-- Dependencies: 241
-- Name: beca_estudiante_id_beca_estudiante_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.beca_estudiante_id_beca_estudiante_seq', 2, true);


--
-- TOC entry 5673 (class 0 OID 0)
-- Dependencies: 221
-- Name: beca_id_beca_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.beca_id_beca_seq', 2, true);


--
-- TOC entry 5674 (class 0 OID 0)
-- Dependencies: 291
-- Name: beca_obligacion_id_beca_obligacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.beca_obligacion_id_beca_obligacion_seq', 1, true);


--
-- TOC entry 5675 (class 0 OID 0)
-- Dependencies: 273
-- Name: cambio_carrera_id_cambio_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.cambio_carrera_id_cambio_seq', 3, true);


--
-- TOC entry 5676 (class 0 OID 0)
-- Dependencies: 243
-- Name: carrera_ciclo_id_carrera_ciclo_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.carrera_ciclo_id_carrera_ciclo_seq', 8, true);


--
-- TOC entry 5677 (class 0 OID 0)
-- Dependencies: 223
-- Name: carrera_id_carrera_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.carrera_id_carrera_seq', 8, true);


--
-- TOC entry 5678 (class 0 OID 0)
-- Dependencies: 225
-- Name: ciclo_escolar_id_ciclo_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.ciclo_escolar_id_ciclo_seq', 5, true);


--
-- TOC entry 5679 (class 0 OID 0)
-- Dependencies: 245
-- Name: contacto_id_contacto_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.contacto_id_contacto_seq', 2, true);


--
-- TOC entry 5680 (class 0 OID 0)
-- Dependencies: 227
-- Name: descuento_id_descuento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.descuento_id_descuento_seq', 3, true);


--
-- TOC entry 5681 (class 0 OID 0)
-- Dependencies: 283
-- Name: descuento_obligacion_id_descuento_obligacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.descuento_obligacion_id_descuento_obligacion_seq', 3, true);


--
-- TOC entry 5682 (class 0 OID 0)
-- Dependencies: 258
-- Name: documento_expediente_id_documento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.documento_expediente_id_documento_seq', 1, true);


--
-- TOC entry 5683 (class 0 OID 0)
-- Dependencies: 229
-- Name: empleado_id_empleado_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.empleado_id_empleado_seq', 3, true);


--
-- TOC entry 5684 (class 0 OID 0)
-- Dependencies: 231
-- Name: estudiante_id_estudiante_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.estudiante_id_estudiante_seq', 8, true);


--
-- TOC entry 5685 (class 0 OID 0)
-- Dependencies: 247
-- Name: evaluacion_id_evaluacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.evaluacion_id_evaluacion_seq', 5, true);


--
-- TOC entry 5686 (class 0 OID 0)
-- Dependencies: 249
-- Name: expediente_id_expediente_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.expediente_id_expediente_seq', 1, true);


--
-- TOC entry 5687 (class 0 OID 0)
-- Dependencies: 260
-- Name: grado_id_grado_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.grado_id_grado_seq', 8, true);


--
-- TOC entry 5688 (class 0 OID 0)
-- Dependencies: 271
-- Name: inscripcion_id_inscripcion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.inscripcion_id_inscripcion_seq', 14, true);


--
-- TOC entry 5689 (class 0 OID 0)
-- Dependencies: 275
-- Name: movimiento_saldo_id_movimiento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.movimiento_saldo_id_movimiento_seq', 6, true);


--
-- TOC entry 5690 (class 0 OID 0)
-- Dependencies: 262
-- Name: notificacion_destinatario_id_destinatario_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.notificacion_destinatario_id_destinatario_seq', 6, true);


--
-- TOC entry 5691 (class 0 OID 0)
-- Dependencies: 233
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.notificacion_id_notificacion_seq', 5, true);


--
-- TOC entry 5692 (class 0 OID 0)
-- Dependencies: 277
-- Name: obligacion_id_obligacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.obligacion_id_obligacion_seq', 31, true);


--
-- TOC entry 5693 (class 0 OID 0)
-- Dependencies: 251
-- Name: pago_id_pago_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.pago_id_pago_seq', 15, true);


--
-- TOC entry 5694 (class 0 OID 0)
-- Dependencies: 235
-- Name: permiso_id_permiso_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.permiso_id_permiso_seq', 21, true);


--
-- TOC entry 5695 (class 0 OID 0)
-- Dependencies: 264
-- Name: precio_carrera_id_precio_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.precio_carrera_id_precio_seq', 9, true);


--
-- TOC entry 5696 (class 0 OID 0)
-- Dependencies: 266
-- Name: recibo_id_recibo_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.recibo_id_recibo_seq', 37, true);


--
-- TOC entry 5697 (class 0 OID 0)
-- Dependencies: 237
-- Name: rol_id_rol_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.rol_id_rol_seq', 2, true);


--
-- TOC entry 5698 (class 0 OID 0)
-- Dependencies: 268
-- Name: saldo_favor_id_saldo_favor_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.saldo_favor_id_saldo_favor_seq', 4, true);


--
-- TOC entry 5699 (class 0 OID 0)
-- Dependencies: 279
-- Name: solvencia_id_solvencia_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.solvencia_id_solvencia_seq', 5, true);


--
-- TOC entry 5700 (class 0 OID 0)
-- Dependencies: 239
-- Name: tipo_documento_id_tipo_documento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.tipo_documento_id_tipo_documento_seq', 4, true);


--
-- TOC entry 5701 (class 0 OID 0)
-- Dependencies: 254
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.usuario_id_usuario_seq', 2, true);


--
-- TOC entry 5229 (class 2606 OID 26735)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 5351 (class 2606 OID 27584)
-- Name: aplicacion_pago aplicacion_pago_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT aplicacion_pago_pkey PRIMARY KEY (id_aplicacion);


--
-- TOC entry 5297 (class 2606 OID 27146)
-- Name: auditoria auditoria_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id_auditoria);


--
-- TOC entry 5270 (class 2606 OID 26944)
-- Name: beca_estudiante beca_estudiante_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT beca_estudiante_pkey PRIMARY KEY (id_beca_estudiante);


--
-- TOC entry 5359 (class 2606 OID 33900)
-- Name: beca_obligacion beca_obligacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_obligacion
    ADD CONSTRAINT beca_obligacion_pkey PRIMARY KEY (id_beca_obligacion);


--
-- TOC entry 5231 (class 2606 OID 26760)
-- Name: beca beca_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca
    ADD CONSTRAINT beca_pkey PRIMARY KEY (id_beca);


--
-- TOC entry 5332 (class 2606 OID 27410)
-- Name: cambio_carrera cambio_carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT cambio_carrera_pkey PRIMARY KEY (id_cambio);


--
-- TOC entry 5272 (class 2606 OID 26968)
-- Name: carrera_ciclo carrera_ciclo_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT carrera_ciclo_pkey PRIMARY KEY (id_carrera_ciclo);


--
-- TOC entry 5235 (class 2606 OID 26779)
-- Name: carrera carrera_nombre_key; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera
    ADD CONSTRAINT carrera_nombre_key UNIQUE (nombre);


--
-- TOC entry 5237 (class 2606 OID 26777)
-- Name: carrera carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera
    ADD CONSTRAINT carrera_pkey PRIMARY KEY (id_carrera);


--
-- TOC entry 5239 (class 2606 OID 26804)
-- Name: ciclo_escolar ciclo_escolar_nombre_key; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.ciclo_escolar
    ADD CONSTRAINT ciclo_escolar_nombre_key UNIQUE (nombre);


--
-- TOC entry 5241 (class 2606 OID 26802)
-- Name: ciclo_escolar ciclo_escolar_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.ciclo_escolar
    ADD CONSTRAINT ciclo_escolar_pkey PRIMARY KEY (id_ciclo);


--
-- TOC entry 5276 (class 2606 OID 26994)
-- Name: contacto contacto_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.contacto
    ADD CONSTRAINT contacto_pkey PRIMARY KEY (id_contacto);


--
-- TOC entry 5357 (class 2606 OID 27611)
-- Name: descuento_obligacion descuento_obligacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT descuento_obligacion_pkey PRIMARY KEY (id_descuento_obligacion);


--
-- TOC entry 5243 (class 2606 OID 26820)
-- Name: descuento descuento_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento
    ADD CONSTRAINT descuento_pkey PRIMARY KEY (id_descuento);


--
-- TOC entry 5301 (class 2606 OID 27169)
-- Name: documento_expediente documento_expediente_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT documento_expediente_pkey PRIMARY KEY (id_documento);


--
-- TOC entry 5247 (class 2606 OID 26836)
-- Name: empleado empleado_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.empleado
    ADD CONSTRAINT empleado_pkey PRIMARY KEY (id_empleado);


--
-- TOC entry 5249 (class 2606 OID 26867)
-- Name: estudiante estudiante_codigo_estudiante_key; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT estudiante_codigo_estudiante_key UNIQUE (codigo_estudiante);


--
-- TOC entry 5251 (class 2606 OID 26869)
-- Name: estudiante estudiante_cui_key; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT estudiante_cui_key UNIQUE (cui);


--
-- TOC entry 5253 (class 2606 OID 26865)
-- Name: estudiante estudiante_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT estudiante_pkey PRIMARY KEY (id_estudiante);


--
-- TOC entry 5279 (class 2606 OID 27014)
-- Name: evaluacion evaluacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.evaluacion
    ADD CONSTRAINT evaluacion_pkey PRIMARY KEY (id_evaluacion);


--
-- TOC entry 5281 (class 2606 OID 27032)
-- Name: expediente expediente_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT expediente_pkey PRIMARY KEY (id_expediente);


--
-- TOC entry 5304 (class 2606 OID 27193)
-- Name: grado grado_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT grado_pkey PRIMARY KEY (id_grado);


--
-- TOC entry 5329 (class 2606 OID 27366)
-- Name: inscripcion inscripcion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT inscripcion_pkey PRIMARY KEY (id_inscripcion);


--
-- TOC entry 5337 (class 2606 OID 27458)
-- Name: movimiento_saldo movimiento_saldo_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT movimiento_saldo_pkey PRIMARY KEY (id_movimiento);


--
-- TOC entry 5308 (class 2606 OID 27214)
-- Name: notificacion_destinatario notificacion_destinatario_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT notificacion_destinatario_pkey PRIMARY KEY (id_destinatario);


--
-- TOC entry 5256 (class 2606 OID 26885)
-- Name: notificacion notificacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion
    ADD CONSTRAINT notificacion_pkey PRIMARY KEY (id_notificacion);


--
-- TOC entry 5342 (class 2606 OID 27513)
-- Name: obligacion obligacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT obligacion_pkey PRIMARY KEY (id_obligacion);


--
-- TOC entry 5287 (class 2606 OID 27078)
-- Name: pago pago_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.pago
    ADD CONSTRAINT pago_pkey PRIMARY KEY (id_pago);


--
-- TOC entry 5258 (class 2606 OID 26896)
-- Name: permiso permiso_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.permiso
    ADD CONSTRAINT permiso_pkey PRIMARY KEY (id_permiso);


--
-- TOC entry 5310 (class 2606 OID 27251)
-- Name: precio_carrera precio_carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.precio_carrera
    ADD CONSTRAINT precio_carrera_pkey PRIMARY KEY (id_precio);


--
-- TOC entry 5312 (class 2606 OID 27269)
-- Name: recibo recibo_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT recibo_pkey PRIMARY KEY (id_recibo);


--
-- TOC entry 5289 (class 2606 OID 27092)
-- Name: rol_permiso rol_permiso_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT rol_permiso_pkey PRIMARY KEY (id_rol, id_permiso);


--
-- TOC entry 5262 (class 2606 OID 26911)
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- TOC entry 5321 (class 2606 OID 27300)
-- Name: saldo_favor saldo_favor_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.saldo_favor
    ADD CONSTRAINT saldo_favor_pkey PRIMARY KEY (id_saldo_favor);


--
-- TOC entry 5347 (class 2606 OID 27552)
-- Name: solvencia solvencia_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT solvencia_pkey PRIMARY KEY (id_solvencia);


--
-- TOC entry 5266 (class 2606 OID 26930)
-- Name: tipo_documento tipo_documento_nombre_key; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.tipo_documento
    ADD CONSTRAINT tipo_documento_nombre_key UNIQUE (nombre);


--
-- TOC entry 5268 (class 2606 OID 26928)
-- Name: tipo_documento tipo_documento_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.tipo_documento
    ADD CONSTRAINT tipo_documento_pkey PRIMARY KEY (id_tipo_documento);


--
-- TOC entry 5355 (class 2606 OID 27586)
-- Name: aplicacion_pago uq_aplicacion_pago_obligacion; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT uq_aplicacion_pago_obligacion UNIQUE (id_pago, id_obligacion);


--
-- TOC entry 5233 (class 2606 OID 26762)
-- Name: beca uq_beca_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca
    ADD CONSTRAINT uq_beca_nombre UNIQUE (nombre);


--
-- TOC entry 5362 (class 2606 OID 33902)
-- Name: beca_obligacion uq_beca_obligacion_obligacion; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_obligacion
    ADD CONSTRAINT uq_beca_obligacion_obligacion UNIQUE (id_obligacion);


--
-- TOC entry 5274 (class 2606 OID 26970)
-- Name: carrera_ciclo uq_carrera_ciclo; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT uq_carrera_ciclo UNIQUE (id_carrera, id_ciclo);


--
-- TOC entry 5245 (class 2606 OID 26822)
-- Name: descuento uq_descuento_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento
    ADD CONSTRAINT uq_descuento_nombre UNIQUE (nombre);


--
-- TOC entry 5283 (class 2606 OID 27034)
-- Name: expediente uq_expediente_estudiante; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT uq_expediente_estudiante UNIQUE (id_estudiante);


--
-- TOC entry 5306 (class 2606 OID 27195)
-- Name: grado uq_grado_carrera_ciclo_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT uq_grado_carrera_ciclo_nombre UNIQUE (id_carrera_ciclo, nombre);


--
-- TOC entry 5260 (class 2606 OID 26898)
-- Name: permiso uq_permiso_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.permiso
    ADD CONSTRAINT uq_permiso_nombre UNIQUE (nombre);


--
-- TOC entry 5314 (class 2606 OID 27271)
-- Name: recibo uq_recibo_codigo; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_codigo UNIQUE (codigo_verificacion);


--
-- TOC entry 5316 (class 2606 OID 27275)
-- Name: recibo uq_recibo_numero; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_numero UNIQUE (numero_recibo);


--
-- TOC entry 5318 (class 2606 OID 27273)
-- Name: recibo uq_recibo_pago; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_pago UNIQUE (id_pago);


--
-- TOC entry 5264 (class 2606 OID 26913)
-- Name: rol uq_rol_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol
    ADD CONSTRAINT uq_rol_nombre UNIQUE (nombre);


--
-- TOC entry 5349 (class 2606 OID 27554)
-- Name: solvencia uq_solvencia_codigo; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT uq_solvencia_codigo UNIQUE (codigo_verificacion);


--
-- TOC entry 5291 (class 2606 OID 27128)
-- Name: usuario uq_usuario_empleado; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT uq_usuario_empleado UNIQUE (id_empleado);


--
-- TOC entry 5293 (class 2606 OID 27126)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 5323 (class 2606 OID 27318)
-- Name: usuario_rol usuario_rol_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT usuario_rol_pkey PRIMARY KEY (id_usuario, id_rol);


--
-- TOC entry 5295 (class 2606 OID 27130)
-- Name: usuario usuario_username_key; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT usuario_username_key UNIQUE (username);


--
-- TOC entry 5352 (class 1259 OID 27597)
-- Name: idx_aplicacion_obligacion; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_aplicacion_obligacion ON school.aplicacion_pago USING btree (id_obligacion);


--
-- TOC entry 5353 (class 1259 OID 27598)
-- Name: idx_aplicacion_pago; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_aplicacion_pago ON school.aplicacion_pago USING btree (id_pago);


--
-- TOC entry 5298 (class 1259 OID 27152)
-- Name: idx_auditoria_fecha; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_auditoria_fecha ON school.auditoria USING btree (fecha_evento);


--
-- TOC entry 5299 (class 1259 OID 27153)
-- Name: idx_auditoria_usuario; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_auditoria_usuario ON school.auditoria USING btree (id_usuario);


--
-- TOC entry 5360 (class 1259 OID 33913)
-- Name: idx_beca_obligacion_beca_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_beca_obligacion_beca_estudiante ON school.beca_obligacion USING btree (id_beca_estudiante);


--
-- TOC entry 5277 (class 1259 OID 27000)
-- Name: idx_contacto_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_contacto_estudiante ON school.contacto USING btree (id_estudiante);


--
-- TOC entry 5302 (class 1259 OID 27180)
-- Name: idx_documento_expediente; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_documento_expediente ON school.documento_expediente USING btree (id_expediente);


--
-- TOC entry 5254 (class 1259 OID 26870)
-- Name: idx_estudiante_activo; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_estudiante_activo ON school.estudiante USING btree (id_estudiante) WHERE (estado = 'ACTIVO'::school.estado_estudiante);


--
-- TOC entry 5324 (class 1259 OID 27382)
-- Name: idx_inscripcion_activa; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_activa ON school.inscripcion USING btree (id_estudiante) WHERE (estado = 'ACTIVA'::school.estado_inscripcion);


--
-- TOC entry 5325 (class 1259 OID 27383)
-- Name: idx_inscripcion_carrera_ciclo; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_carrera_ciclo ON school.inscripcion USING btree (id_carrera_ciclo);


--
-- TOC entry 5326 (class 1259 OID 27384)
-- Name: idx_inscripcion_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_estudiante ON school.inscripcion USING btree (id_estudiante);


--
-- TOC entry 5327 (class 1259 OID 27385)
-- Name: idx_inscripcion_grado; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_grado ON school.inscripcion USING btree (id_grado);


--
-- TOC entry 5333 (class 1259 OID 27474)
-- Name: idx_movimiento_destino; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_movimiento_destino ON school.movimiento_saldo USING btree (id_inscripcion_destino);


--
-- TOC entry 5334 (class 1259 OID 27475)
-- Name: idx_movimiento_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_movimiento_estudiante ON school.movimiento_saldo USING btree (id_estudiante);


--
-- TOC entry 5335 (class 1259 OID 27476)
-- Name: idx_movimiento_origen; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_movimiento_origen ON school.movimiento_saldo USING btree (id_inscripcion_origen);


--
-- TOC entry 5338 (class 1259 OID 27524)
-- Name: idx_obligacion_fecha_vencimiento; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_obligacion_fecha_vencimiento ON school.obligacion USING btree (fecha_vencimiento);


--
-- TOC entry 5339 (class 1259 OID 27525)
-- Name: idx_obligacion_inscripcion; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_obligacion_inscripcion ON school.obligacion USING btree (id_inscripcion);


--
-- TOC entry 5340 (class 1259 OID 27526)
-- Name: idx_obligacion_pendiente; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_obligacion_pendiente ON school.obligacion USING btree (id_inscripcion) WHERE (estado = ANY (ARRAY['PENDIENTE'::school.estado_obligacion, 'PARCIAL'::school.estado_obligacion]));


--
-- TOC entry 5284 (class 1259 OID 27084)
-- Name: idx_pago_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_pago_estudiante ON school.pago USING btree (id_estudiante);


--
-- TOC entry 5285 (class 1259 OID 27085)
-- Name: idx_pago_fecha; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_pago_fecha ON school.pago USING btree (fecha_pago);


--
-- TOC entry 5319 (class 1259 OID 27311)
-- Name: idx_saldo_favor_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_saldo_favor_estudiante ON school.saldo_favor USING btree (id_estudiante) WHERE ((estado)::text = 'ACTIVO'::text);


--
-- TOC entry 5344 (class 1259 OID 27570)
-- Name: idx_solvencia_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_solvencia_estudiante ON school.solvencia USING btree (id_estudiante);


--
-- TOC entry 5345 (class 1259 OID 27571)
-- Name: idx_solvencia_evaluacion; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_solvencia_evaluacion ON school.solvencia USING btree (id_evaluacion);


--
-- TOC entry 5330 (class 1259 OID 27386)
-- Name: uq_inscripcion_activa_estudiante_ciclo; Type: INDEX; Schema: school; Owner: postgres
--

CREATE UNIQUE INDEX uq_inscripcion_activa_estudiante_ciclo ON school.inscripcion USING btree (id_estudiante, id_carrera_ciclo) WHERE (estado = 'ACTIVA'::school.estado_inscripcion);


--
-- TOC entry 5343 (class 1259 OID 27527)
-- Name: uq_obligacion_mensualidad_periodo; Type: INDEX; Schema: school; Owner: postgres
--

CREATE UNIQUE INDEX uq_obligacion_mensualidad_periodo ON school.obligacion USING btree (id_inscripcion, periodo) WHERE ((tipo_obligacion)::text = 'MENSUALIDAD'::text);


--
-- TOC entry 5560 (class 2618 OID 27625)
-- Name: vw_saldo_obligaciones _RETURN; Type: RULE; Schema: school; Owner: postgres
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
        CASE
            WHEN (o.estado = 'ANULADA'::school.estado_obligacion) THEN (0)::numeric
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


--
-- TOC entry 5409 (class 2620 OID 27675)
-- Name: aplicacion_pago trg_actualizar_estado_obligacion; Type: TRIGGER; Schema: school; Owner: postgres
--

CREATE TRIGGER trg_actualizar_estado_obligacion AFTER INSERT OR DELETE OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_trigger_actualizar_obligacion();


--
-- TOC entry 5406 (class 2620 OID 27676)
-- Name: pago trg_recalcular_obligaciones_pago_anulado; Type: TRIGGER; Schema: school; Owner: postgres
--

CREATE TRIGGER trg_recalcular_obligaciones_pago_anulado AFTER UPDATE ON school.pago FOR EACH ROW EXECUTE FUNCTION school.fn_recalcular_obligaciones_pago_anulado();


--
-- TOC entry 5410 (class 2620 OID 27677)
-- Name: aplicacion_pago trg_validar_aplicacion_pago; Type: TRIGGER; Schema: school; Owner: postgres
--

CREATE TRIGGER trg_validar_aplicacion_pago BEFORE INSERT OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_validar_aplicacion_pago();


--
-- TOC entry 5412 (class 2620 OID 27678)
-- Name: descuento_obligacion trg_validar_descuentos_obligacion; Type: TRIGGER; Schema: school; Owner: postgres
--

CREATE TRIGGER trg_validar_descuentos_obligacion BEFORE INSERT OR UPDATE ON school.descuento_obligacion FOR EACH ROW EXECUTE FUNCTION school.fn_validar_descuentos_obligacion();


--
-- TOC entry 5407 (class 2620 OID 27679)
-- Name: inscripcion trg_validar_grado_inscripcion; Type: TRIGGER; Schema: school; Owner: postgres
--

CREATE TRIGGER trg_validar_grado_inscripcion BEFORE INSERT OR UPDATE ON school.inscripcion FOR EACH ROW EXECUTE FUNCTION school.fn_validar_grado_inscripcion();


--
-- TOC entry 5408 (class 2620 OID 27680)
-- Name: movimiento_saldo trg_validar_movimiento_saldo; Type: TRIGGER; Schema: school; Owner: postgres
--

CREATE TRIGGER trg_validar_movimiento_saldo BEFORE INSERT OR UPDATE ON school.movimiento_saldo FOR EACH ROW EXECUTE FUNCTION school.fn_validar_movimiento_saldo();


--
-- TOC entry 5411 (class 2620 OID 27681)
-- Name: aplicacion_pago trg_validar_propietario_pago_obligacion; Type: TRIGGER; Schema: school; Owner: postgres
--

CREATE TRIGGER trg_validar_propietario_pago_obligacion BEFORE INSERT OR UPDATE ON school.aplicacion_pago FOR EACH ROW EXECUTE FUNCTION school.fn_validar_propietario_pago_obligacion();


--
-- TOC entry 5365 (class 2606 OID 26971)
-- Name: carrera_ciclo carrera_ciclo_id_carrera_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT carrera_ciclo_id_carrera_fkey FOREIGN KEY (id_carrera) REFERENCES school.carrera(id_carrera) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5366 (class 2606 OID 26976)
-- Name: carrera_ciclo carrera_ciclo_id_ciclo_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT carrera_ciclo_id_ciclo_fkey FOREIGN KEY (id_ciclo) REFERENCES school.ciclo_escolar(id_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5367 (class 2606 OID 26995)
-- Name: contacto contacto_id_estudiante_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.contacto
    ADD CONSTRAINT contacto_id_estudiante_fkey FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5375 (class 2606 OID 27170)
-- Name: documento_expediente documento_expediente_id_expediente_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT documento_expediente_id_expediente_fkey FOREIGN KEY (id_expediente) REFERENCES school.expediente(id_expediente) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5376 (class 2606 OID 27175)
-- Name: documento_expediente documento_expediente_id_tipo_documento_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT documento_expediente_id_tipo_documento_fkey FOREIGN KEY (id_tipo_documento) REFERENCES school.tipo_documento(id_tipo_documento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5369 (class 2606 OID 27035)
-- Name: expediente expediente_id_estudiante_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT expediente_id_estudiante_fkey FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5400 (class 2606 OID 27587)
-- Name: aplicacion_pago fk_aplicacion_obligacion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT fk_aplicacion_obligacion FOREIGN KEY (id_obligacion) REFERENCES school.obligacion(id_obligacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5401 (class 2606 OID 27592)
-- Name: aplicacion_pago fk_aplicacion_pago; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT fk_aplicacion_pago FOREIGN KEY (id_pago) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5374 (class 2606 OID 27147)
-- Name: auditoria fk_auditoria_usuario; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.auditoria
    ADD CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES school.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 5363 (class 2606 OID 26945)
-- Name: beca_estudiante fk_beca_estudiante_beca; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT fk_beca_estudiante_beca FOREIGN KEY (id_beca) REFERENCES school.beca(id_beca) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5364 (class 2606 OID 26950)
-- Name: beca_estudiante fk_beca_estudiante_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT fk_beca_estudiante_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5404 (class 2606 OID 33903)
-- Name: beca_obligacion fk_beca_obligacion_beca_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_obligacion
    ADD CONSTRAINT fk_beca_obligacion_beca_estudiante FOREIGN KEY (id_beca_estudiante) REFERENCES school.beca_estudiante(id_beca_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5405 (class 2606 OID 33908)
-- Name: beca_obligacion fk_beca_obligacion_obligacion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_obligacion
    ADD CONSTRAINT fk_beca_obligacion_obligacion FOREIGN KEY (id_obligacion) REFERENCES school.obligacion(id_obligacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5389 (class 2606 OID 27411)
-- Name: cambio_carrera fk_cambio_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5390 (class 2606 OID 27416)
-- Name: cambio_carrera fk_cambio_inscripcion_destino; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_inscripcion_destino FOREIGN KEY (id_inscripcion_destino) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5391 (class 2606 OID 27421)
-- Name: cambio_carrera fk_cambio_inscripcion_origen; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_inscripcion_origen FOREIGN KEY (id_inscripcion_origen) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5402 (class 2606 OID 27612)
-- Name: descuento_obligacion fk_descuento_obligacion_descuento; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT fk_descuento_obligacion_descuento FOREIGN KEY (id_descuento) REFERENCES school.descuento(id_descuento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5403 (class 2606 OID 27617)
-- Name: descuento_obligacion fk_descuento_obligacion_obligacion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT fk_descuento_obligacion_obligacion FOREIGN KEY (id_obligacion) REFERENCES school.obligacion(id_obligacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5368 (class 2606 OID 27015)
-- Name: evaluacion fk_evaluacion_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.evaluacion
    ADD CONSTRAINT fk_evaluacion_ciclo FOREIGN KEY (id_ciclo) REFERENCES school.ciclo_escolar(id_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5392 (class 2606 OID 27464)
-- Name: movimiento_saldo fk_movimiento_destino; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_destino FOREIGN KEY (id_inscripcion_destino) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5393 (class 2606 OID 27459)
-- Name: movimiento_saldo fk_movimiento_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5394 (class 2606 OID 27469)
-- Name: movimiento_saldo fk_movimiento_origen; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_origen FOREIGN KEY (id_inscripcion_origen) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5378 (class 2606 OID 27215)
-- Name: notificacion_destinatario fk_notificacion_contacto; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT fk_notificacion_contacto FOREIGN KEY (id_contacto) REFERENCES school.contacto(id_contacto) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5379 (class 2606 OID 27220)
-- Name: notificacion_destinatario fk_notificacion_destinatario; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT fk_notificacion_destinatario FOREIGN KEY (id_notificacion) REFERENCES school.notificacion(id_notificacion) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 5395 (class 2606 OID 27514)
-- Name: obligacion fk_obligacion_inscripcion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT fk_obligacion_inscripcion FOREIGN KEY (id_inscripcion) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5396 (class 2606 OID 27519)
-- Name: obligacion fk_obligacion_precio; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT fk_obligacion_precio FOREIGN KEY (id_precio) REFERENCES school.precio_carrera(id_precio) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5370 (class 2606 OID 27079)
-- Name: pago fk_pago_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.pago
    ADD CONSTRAINT fk_pago_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5380 (class 2606 OID 27252)
-- Name: precio_carrera fk_precio_carrera_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.precio_carrera
    ADD CONSTRAINT fk_precio_carrera_ciclo FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5381 (class 2606 OID 27276)
-- Name: recibo fk_recibo_pago; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT fk_recibo_pago FOREIGN KEY (id_pago) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5371 (class 2606 OID 27093)
-- Name: rol_permiso fk_rol_permiso_permiso; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT fk_rol_permiso_permiso FOREIGN KEY (id_permiso) REFERENCES school.permiso(id_permiso) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5372 (class 2606 OID 27098)
-- Name: rol_permiso fk_rol_permiso_rol; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT fk_rol_permiso_rol FOREIGN KEY (id_rol) REFERENCES school.rol(id_rol) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5382 (class 2606 OID 27301)
-- Name: saldo_favor fk_saldo_favor_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.saldo_favor
    ADD CONSTRAINT fk_saldo_favor_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5383 (class 2606 OID 27306)
-- Name: saldo_favor fk_saldo_favor_pago; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.saldo_favor
    ADD CONSTRAINT fk_saldo_favor_pago FOREIGN KEY (id_pago_origen) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5397 (class 2606 OID 27555)
-- Name: solvencia fk_solvencia_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5398 (class 2606 OID 27560)
-- Name: solvencia fk_solvencia_evaluacion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_evaluacion FOREIGN KEY (id_evaluacion) REFERENCES school.evaluacion(id_evaluacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5399 (class 2606 OID 27565)
-- Name: solvencia fk_solvencia_inscripcion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_inscripcion FOREIGN KEY (id_inscripcion) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5373 (class 2606 OID 27131)
-- Name: usuario fk_usuario_empleado; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT fk_usuario_empleado FOREIGN KEY (id_empleado) REFERENCES school.empleado(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5384 (class 2606 OID 27319)
-- Name: usuario_rol fk_usuario_rol_rol; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_rol FOREIGN KEY (id_rol) REFERENCES school.rol(id_rol) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5385 (class 2606 OID 27324)
-- Name: usuario_rol fk_usuario_rol_usuario; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_usuario FOREIGN KEY (id_usuario) REFERENCES school.usuario(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5377 (class 2606 OID 27196)
-- Name: grado grado_id_carrera_ciclo_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT grado_id_carrera_ciclo_fkey FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5386 (class 2606 OID 27367)
-- Name: inscripcion inscripcion_id_carrera_ciclo_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT inscripcion_id_carrera_ciclo_fkey FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5387 (class 2606 OID 27372)
-- Name: inscripcion inscripcion_id_estudiante_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT inscripcion_id_estudiante_fkey FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5388 (class 2606 OID 27377)
-- Name: inscripcion inscripcion_id_grado_fkey; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT inscripcion_id_grado_fkey FOREIGN KEY (id_grado) REFERENCES school.grado(id_grado) ON UPDATE CASCADE ON DELETE RESTRICT;


-- Completed on 2026-09-29 08:33:31

--
-- PostgreSQL database dump complete
--

\unrestrict rGFKUzRb1wSZn96QRbGXinkhnINTB4Tkdz17gHAlUWlEtEs3GObSziPnMdK32fG

