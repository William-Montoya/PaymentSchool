\set ON_ERROR_STOP on
\echo '=== PaymentSchool: pruebas funcionales de integridad ==='
\echo 'La transaccion se revierte al final; no deja datos de prueba.'

BEGIN;
SET LOCAL search_path = school, public;

DO $$
DECLARE
    v_ciclo BIGINT;
    v_carrera_a BIGINT;
    v_carrera_b BIGINT;
    v_cc_a BIGINT;
    v_cc_b BIGINT;
    v_grado_a BIGINT;
    v_grado_b BIGINT;
    v_est1 BIGINT;
    v_est2 BIGINT;
    v_ins1 BIGINT;
    v_ins2 BIGINT;
    v_precio_a BIGINT;
    v_precio_b BIGINT;
    v_eval BIGINT;
    v_ob1 BIGINT;
    v_ob2 BIGINT;
    v_ob3 BIGINT;
    v_ob4 BIGINT;
    v_ob_e2 BIGINT;
    v_pago1 BIGINT;
    v_pago2 BIGINT;
    v_pago_auto BIGINT;
    v_saldo_favor BIGINT;
    v_descuento BIGINT;
    v_solvencia BIGINT;
    v_cambio BIGINT;
    v_ins_destino BIGINT;
    v_movimiento BIGINT;
    v_recibo BIGINT;
    v_count INTEGER;
    v_num NUMERIC(12,2);
    v_estado TEXT;
    v_msg TEXT;
    v_beca BIGINT;
    v_beca_estudiante BIGINT;
    v_beca_obligacion BIGINT;
BEGIN
    RAISE NOTICE '01/12 Creando datos base...';

    INSERT INTO ciclo_escolar (nombre, fecha_inicio, fecha_fin, estado)
    VALUES ('TST-CICLO-2026', DATE '2026-01-01', DATE '2026-12-31', 'ACTIVO')
    RETURNING id_ciclo INTO v_ciclo;

    INSERT INTO carrera (nombre, descripcion)
    VALUES ('TST-CARRERA-A', 'Carrera de prueba A')
    RETURNING id_carrera INTO v_carrera_a;

    INSERT INTO carrera (nombre, descripcion)
    VALUES ('TST-CARRERA-B', 'Carrera de prueba B')
    RETURNING id_carrera INTO v_carrera_b;

    INSERT INTO carrera_ciclo (id_carrera, id_ciclo, nombre_comercial)
    VALUES (v_carrera_a, v_ciclo, 'TST A 2026')
    RETURNING id_carrera_ciclo INTO v_cc_a;

    INSERT INTO carrera_ciclo (id_carrera, id_ciclo, nombre_comercial)
    VALUES (v_carrera_b, v_ciclo, 'TST B 2026')
    RETURNING id_carrera_ciclo INTO v_cc_b;

    INSERT INTO grado (id_carrera_ciclo, nombre, nivel_orden)
    VALUES (v_cc_a, 'TST Grado A', 1)
    RETURNING id_grado INTO v_grado_a;

    INSERT INTO grado (id_carrera_ciclo, nombre, nivel_orden)
    VALUES (v_cc_b, 'TST Grado B', 1)
    RETURNING id_grado INTO v_grado_b;

    INSERT INTO estudiante (codigo_estudiante, nombres, apellidos)
    VALUES ('TST-E001', 'Alumno', 'Prueba Uno')
    RETURNING id_estudiante INTO v_est1;

    INSERT INTO estudiante (codigo_estudiante, nombres, apellidos)
    VALUES ('TST-E002', 'Alumno', 'Prueba Dos')
    RETURNING id_estudiante INTO v_est2;

    INSERT INTO inscripcion (id_estudiante, id_carrera_ciclo, id_grado)
    VALUES (v_est1, v_cc_a, v_grado_a)
    RETURNING id_inscripcion INTO v_ins1;

    INSERT INTO inscripcion (id_estudiante, id_carrera_ciclo, id_grado)
    VALUES (v_est2, v_cc_a, v_grado_a)
    RETURNING id_inscripcion INTO v_ins2;

    INSERT INTO precio_carrera (
        id_carrera_ciclo, tipo, concepto, monto, fecha_inicio, fecha_fin
    ) VALUES (
        v_cc_a, 'MENSUALIDAD', 'TST Mensualidad A', 1000.00,
        DATE '2026-01-01', DATE '2026-12-31'
    ) RETURNING id_precio INTO v_precio_a;

    INSERT INTO precio_carrera (
        id_carrera_ciclo, tipo, concepto, monto, fecha_inicio, fecha_fin
    ) VALUES (
        v_cc_b, 'MENSUALIDAD', 'TST Mensualidad B', 1200.00,
        DATE '2026-01-01', DATE '2026-12-31'
    ) RETURNING id_precio INTO v_precio_b;

    INSERT INTO evaluacion (
        id_ciclo, nombre, fecha_evaluacion, fecha_corte_finanzas
    ) VALUES (
        v_ciclo, 'TST Evaluacion Final', DATE '2026-12-15', DATE '2026-12-31'
    ) RETURNING id_evaluacion INTO v_eval;

    RAISE NOTICE '02/12 Validando trigger grado/carrera-ciclo...';
    BEGIN
        INSERT INTO inscripcion (id_estudiante, id_carrera_ciclo, id_grado)
        VALUES (v_est2, v_cc_b, v_grado_a);
        RAISE EXCEPTION 'TEST_FAIL: se permitio un grado de otra carrera/ciclo';
    EXCEPTION
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS v_msg = MESSAGE_TEXT;
            IF v_msg = 'TEST_FAIL: se permitio un grado de otra carrera/ciclo' THEN
                RAISE;
            END IF;
            IF POSITION('no pertenece a la carrera/ciclo' IN v_msg) = 0 THEN
                RAISE;
            END IF;
    END;

    RAISE NOTICE '03/12 Generando mensualidades...';
    PERFORM fn_generar_obligaciones_mensuales(
        v_ins1, v_precio_a, DATE '2026-01-05', 3
    );

    SELECT COUNT(*) INTO v_count
    FROM obligacion
    WHERE id_inscripcion = v_ins1
      AND tipo_obligacion = 'MENSUALIDAD';

    IF v_count <> 3 THEN
        RAISE EXCEPTION 'TEST_FAIL: se esperaban 3 mensualidades y existen %', v_count;
    END IF;

    SELECT id_obligacion INTO v_ob1
    FROM obligacion
    WHERE id_inscripcion = v_ins1 AND periodo = '2026-01';

    SELECT id_obligacion INTO v_ob2
    FROM obligacion
    WHERE id_inscripcion = v_ins1 AND periodo = '2026-02';

    SELECT id_obligacion INTO v_ob3
    FROM obligacion
    WHERE id_inscripcion = v_ins1 AND periodo = '2026-03';

    BEGIN
        PERFORM fn_generar_obligaciones_mensuales(
            v_ins1, v_precio_a, DATE '2026-01-05', 1
        );
        RAISE EXCEPTION 'TEST_FAIL: se permitio mensualidad duplicada';
    EXCEPTION
        WHEN unique_violation THEN
            NULL;
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS v_msg = MESSAGE_TEXT;
            IF v_msg = 'TEST_FAIL: se permitio mensualidad duplicada' THEN
                RAISE;
            END IF;
            RAISE;
    END;

    RAISE NOTICE '04/12 Registrando y aplicando pago parcial...';
    v_pago1 := fn_registrar_pago(
        v_est1, 1200.00, 'EFECTIVO', 'TST-PAGO-1', 'Prueba manual', NULL
    );

    PERFORM fn_aplicar_pago(v_pago1, v_ob1, 1000.00);
    PERFORM fn_aplicar_pago(v_pago1, v_ob2, 200.00);

    SELECT estado::text INTO v_estado FROM obligacion WHERE id_obligacion = v_ob1;
    IF v_estado <> 'PAGADA' THEN
        RAISE EXCEPTION 'TEST_FAIL: obligacion 1 deberia estar PAGADA y esta %', v_estado;
    END IF;

    SELECT estado::text INTO v_estado FROM obligacion WHERE id_obligacion = v_ob2;
    IF v_estado <> 'PARCIAL' THEN
        RAISE EXCEPTION 'TEST_FAIL: obligacion 2 deberia estar PARCIAL y esta %', v_estado;
    END IF;

    BEGIN
        PERFORM fn_aplicar_pago(v_pago1, v_ob2, 1.00);
        RAISE EXCEPTION 'TEST_FAIL: se permitio exceder el saldo disponible del pago';
    EXCEPTION
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS v_msg = MESSAGE_TEXT;
            IF v_msg = 'TEST_FAIL: se permitio exceder el saldo disponible del pago' THEN
                RAISE;
            END IF;
            IF POSITION('excede el saldo disponible del pago' IN v_msg) = 0 THEN
                RAISE;
            END IF;
    END;

    RAISE NOTICE '05/12 Validando propietario pago/obligacion...';
    v_pago2 := fn_registrar_pago(
        v_est2, 100.00, 'EFECTIVO', 'TST-PAGO-2', 'Pago estudiante 2', NULL
    );

    BEGIN
        PERFORM fn_aplicar_pago(v_pago2, v_ob2, 50.00);
        RAISE EXCEPTION 'TEST_FAIL: se permitio aplicar pago de otro estudiante';
    EXCEPTION
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS v_msg = MESSAGE_TEXT;
            IF v_msg = 'TEST_FAIL: se permitio aplicar pago de otro estudiante' THEN
                RAISE;
            END IF;
            IF POSITION('otro estudiante' IN v_msg) = 0 THEN
                RAISE;
            END IF;
    END;

    RAISE NOTICE '06/12 Pago automatico y saldo a favor...';
    v_pago_auto := fn_registrar_pago_automatico(
        v_est1, 2500.00, 'TRANSFERENCIA', 'TST-AUTO-1', 'Pago automatico', NULL
    );

    SELECT id_saldo_favor, monto_disponible
    INTO v_saldo_favor, v_num
    FROM saldo_favor
    WHERE id_pago_origen = v_pago_auto;

    IF v_saldo_favor IS NULL OR v_num <> 700.00 THEN
        RAISE EXCEPTION 'TEST_FAIL: saldo a favor esperado 700.00, obtenido %', v_num;
    END IF;

    SELECT COALESCE(SUM(saldo), 0) INTO v_num
    FROM vw_saldo_obligaciones
    WHERE id_inscripcion = v_ins1;

    IF v_num <> 0.00 THEN
        RAISE EXCEPTION 'TEST_FAIL: deuda luego del pago automatico deberia ser 0 y es %', v_num;
    END IF;

    RAISE NOTICE '07/12 Aplicando saldo a favor y generando recibo...';
    INSERT INTO obligacion (
        id_inscripcion, concepto, periodo, fecha_vencimiento,
        monto_bruto, monto_neto, tipo_obligacion
    ) VALUES (
        v_ins1, 'TST Cargo adicional', '2026-04', DATE '2026-04-05',
        500.00, 500.00, 'OTRO'
    ) RETURNING id_obligacion INTO v_ob4;

    PERFORM fn_aplicar_saldo_favor(v_saldo_favor, v_ob4, 500.00);

    SELECT monto_disponible INTO v_num
    FROM saldo_favor
    WHERE id_saldo_favor = v_saldo_favor;

    IF v_num <> 200.00 THEN
        RAISE EXCEPTION 'TEST_FAIL: saldo a favor restante deberia ser 200.00 y es %', v_num;
    END IF;

    SELECT estado::text INTO v_estado FROM obligacion WHERE id_obligacion = v_ob4;
    IF v_estado <> 'PAGADA' THEN
        RAISE EXCEPTION 'TEST_FAIL: cargo adicional deberia estar PAGADA y esta %', v_estado;
    END IF;

    v_recibo := fn_generar_recibo(v_pago1);
    IF NOT EXISTS (SELECT 1 FROM recibo WHERE id_recibo = v_recibo AND id_pago = v_pago1) THEN
        RAISE EXCEPTION 'TEST_FAIL: no se genero correctamente el recibo';
    END IF;

    RAISE NOTICE '08/12 Anulando pago y recalculando obligaciones...';
    PERFORM fn_anular_pago(v_pago_auto, 'Prueba de anulacion', NULL);

    SELECT estado::text INTO v_estado FROM pago WHERE id_pago = v_pago_auto;
    IF v_estado <> 'ANULADO' THEN
        RAISE EXCEPTION 'TEST_FAIL: pago automatico deberia estar ANULADO';
    END IF;

    SELECT estado::text INTO v_estado FROM obligacion WHERE id_obligacion = v_ob2;
    IF v_estado <> 'PARCIAL' THEN
        RAISE EXCEPTION 'TEST_FAIL: obligacion 2 deberia volver a PARCIAL y esta %', v_estado;
    END IF;

    SELECT estado::text INTO v_estado FROM obligacion WHERE id_obligacion = v_ob3;
    IF v_estado <> 'PENDIENTE' THEN
        RAISE EXCEPTION 'TEST_FAIL: obligacion 3 deberia volver a PENDIENTE y esta %', v_estado;
    END IF;

    SELECT estado::text INTO v_estado FROM obligacion WHERE id_obligacion = v_ob4;
    IF v_estado <> 'PENDIENTE' THEN
        RAISE EXCEPTION 'TEST_FAIL: cargo adicional deberia volver a PENDIENTE y esta %', v_estado;
    END IF;

    SELECT estado INTO v_estado FROM saldo_favor WHERE id_saldo_favor = v_saldo_favor;
    SELECT monto_disponible INTO v_num FROM saldo_favor WHERE id_saldo_favor = v_saldo_favor;
    IF v_estado <> 'ANULADO' OR v_num <> 0.00 THEN
        RAISE EXCEPTION 'TEST_FAIL: saldo a favor del pago anulado no quedo ANULADO/0';
    END IF;

    RAISE NOTICE '09/12 Becas y descuentos...';
    INSERT INTO obligacion (
        id_inscripcion, concepto, periodo, fecha_vencimiento,
        monto_bruto, monto_neto, tipo_obligacion
    ) VALUES (
        v_ins2, 'TST Obligacion estudiante 2', 'TST-DESC', DATE '2026-06-01',
        1000.00, 1000.00, 'OTRO'
    ) RETURNING id_obligacion INTO v_ob_e2;

    INSERT INTO descuento (nombre, porcentaje)
    VALUES ('TST Descuento 10%', 10.00)
    RETURNING id_descuento INTO v_descuento;
    
    INSERT INTO beca (
        nombre,
        porcentaje,
        estado,
        fecha_inicio,
        fecha_fin
    )
    VALUES (
        'TST Beca 20%',
        20.00,
        'ACTIVA',
        DATE '2026-01-01',
        DATE '2026-12-31'
    )
    RETURNING id_beca
    INTO v_beca;


    INSERT INTO beca_estudiante (
        id_beca,
        id_estudiante,
        fecha_inicio,
        fecha_fin
    )
    VALUES (
        v_beca,
        v_est2,
        DATE '2026-01-01',
        DATE '2026-12-31'
    )
    RETURNING id_beca_estudiante
    INTO v_beca_estudiante;

    PERFORM fn_aplicar_descuento_obligacion(v_ob_e2, v_descuento);
    v_beca_obligacion :=
        fn_aplicar_beca_estudiante_obligacion(
            v_beca_estudiante,
            v_ob_e2
        );

    IF NOT EXISTS (
        SELECT 1
        FROM beca_obligacion
        WHERE id_beca_obligacion =
            v_beca_obligacion
        AND id_beca_estudiante =
            v_beca_estudiante
        AND id_obligacion =
            v_ob_e2
        AND porcentaje_aplicado = 20.00
        AND monto_aplicado = 200.00
    ) THEN
        RAISE EXCEPTION
            'TEST_FAIL: no se registro correctamente la trazabilidad de beca';
    END IF;

    SELECT monto_neto INTO v_num FROM obligacion WHERE id_obligacion = v_ob_e2;
    IF v_num <> 700.00 THEN
        RAISE EXCEPTION 'TEST_FAIL: monto neto esperado 700.00 tras descuento+beca, obtenido %', v_num;
    END IF;

    RAISE NOTICE '10/12 Solvencia y validacion estudiante/inscripcion/ciclo...';
    v_solvencia := fn_generar_solvencia(v_est1, v_ins1, v_eval);

    SELECT saldo_corte, estado::text INTO v_num, v_estado
    FROM solvencia WHERE id_solvencia = v_solvencia;

    IF v_num <> 2300.00 OR v_estado <> 'INSOLVENTE' THEN
        RAISE EXCEPTION 'TEST_FAIL: solvencia esperada INSOLVENTE/2300.00, obtenida %/%', v_estado, v_num;
    END IF;

    BEGIN
        PERFORM fn_generar_solvencia(v_est2, v_ins1, v_eval);
        RAISE EXCEPTION 'TEST_FAIL: se genero solvencia con estudiante incorrecto';
    EXCEPTION
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS v_msg = MESSAGE_TEXT;
            IF v_msg = 'TEST_FAIL: se genero solvencia con estudiante incorrecto' THEN
                RAISE;
            END IF;
            IF POSITION('no pertenece al estudiante' IN v_msg) = 0 THEN
                RAISE;
            END IF;
    END;

    RAISE NOTICE '11/12 Cambio de carrera y movimiento de saldo...';
    v_cambio := fn_cambiar_carrera(
        v_est1, v_ins1, v_cc_b, v_grado_b, 'Cambio de prueba', NULL
    );

    SELECT id_inscripcion_destino INTO v_ins_destino
    FROM cambio_carrera WHERE id_cambio = v_cambio;

    SELECT estado::text INTO v_estado FROM inscripcion WHERE id_inscripcion = v_ins1;
    IF v_estado <> 'FINALIZADA' THEN
        RAISE EXCEPTION 'TEST_FAIL: inscripcion origen deberia quedar FINALIZADA';
    END IF;

    SELECT estado::text INTO v_estado FROM inscripcion WHERE id_inscripcion = v_ins_destino;
    IF v_estado <> 'ACTIVA' THEN
        RAISE EXCEPTION 'TEST_FAIL: inscripcion destino deberia quedar ACTIVA';
    END IF;

    v_movimiento := fn_trasladar_saldo(
        v_est1, v_ins1, v_ins_destino, 100.00, 'Movimiento de prueba', NULL
    );

    IF NOT EXISTS (
        SELECT 1 FROM movimiento_saldo
        WHERE id_movimiento = v_movimiento
          AND estado = 'APLICADO'
          AND tipo = 'TRASLADO_SALDO'
    ) THEN
        RAISE EXCEPTION 'TEST_FAIL: movimiento de saldo no fue registrado correctamente';
    END IF;

    BEGIN
        PERFORM fn_trasladar_saldo(
            v_est1, v_ins1, v_ins2, 10.00, 'Movimiento invalido', NULL
        );
        RAISE EXCEPTION 'TEST_FAIL: se permitio movimiento hacia inscripcion de otro estudiante';
    EXCEPTION
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS v_msg = MESSAGE_TEXT;
            IF v_msg = 'TEST_FAIL: se permitio movimiento hacia inscripcion de otro estudiante' THEN
                RAISE;
            END IF;
            IF POSITION('destino no pertenece al estudiante' IN v_msg) = 0 THEN
                RAISE;
            END IF;
    END;

    RAISE NOTICE '12/12 Validando vistas principales...';
    IF NOT EXISTS (SELECT 1 FROM vw_dashboard_financiero) THEN
        RAISE EXCEPTION 'TEST_FAIL: vw_dashboard_financiero no devuelve fila';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM vw_estado_cuenta_estudiante
        WHERE id_estudiante = v_est1
    ) THEN
        RAISE EXCEPTION 'TEST_FAIL: vw_estado_cuenta_estudiante no muestra al estudiante de prueba';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM vw_deuda_por_estudiante
        WHERE id_estudiante = v_est2 AND deuda_total > 0
    ) THEN
        RAISE EXCEPTION 'TEST_FAIL: vw_deuda_por_estudiante no refleja deuda activa del estudiante 2';
    END IF;

    RAISE NOTICE '==============================================';
    RAISE NOTICE 'TODAS LAS PRUEBAS FUNCIONALES PASARON';
    RAISE NOTICE 'La transaccion sera revertida (ROLLBACK).';
    RAISE NOTICE '==============================================';
END;
$$;

ROLLBACK;
\echo '=== Fin: no se conservaron datos de prueba ==='
