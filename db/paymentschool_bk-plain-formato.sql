--
-- PostgreSQL database dump
--

\restrict IqAxzaISGSYKbEmSNcbzWvO14gJcvrnUJAWn4VWbpQyUSQgvUirikRYOhqTiyne

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-09-07 21:56:28

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
-- TOC entry 6 (class 2615 OID 24578)
-- Name: school; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA school;


ALTER SCHEMA school OWNER TO postgres;

--
-- TOC entry 944 (class 1247 OID 24654)
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
-- TOC entry 956 (class 1247 OID 24688)
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
-- TOC entry 923 (class 1247 OID 24590)
-- Name: estado_ciclo; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_ciclo AS ENUM (
    'PLANIFICADO',
    'ACTIVO',
    'CERRADO'
);


ALTER TYPE school.estado_ciclo OWNER TO postgres;

--
-- TOC entry 920 (class 1247 OID 24580)
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
-- TOC entry 929 (class 1247 OID 24606)
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
-- TOC entry 953 (class 1247 OID 24680)
-- Name: estado_movimiento_saldo; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_movimiento_saldo AS ENUM (
    'PENDIENTE',
    'APLICADO',
    'ANULADO'
);


ALTER TYPE school.estado_movimiento_saldo OWNER TO postgres;

--
-- TOC entry 935 (class 1247 OID 24624)
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
-- TOC entry 938 (class 1247 OID 24634)
-- Name: estado_pago; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_pago AS ENUM (
    'PENDIENTE',
    'CONFIRMADO',
    'ANULADO'
);


ALTER TYPE school.estado_pago OWNER TO postgres;

--
-- TOC entry 947 (class 1247 OID 24664)
-- Name: estado_solvencia; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_solvencia AS ENUM (
    'SOLVENTE',
    'INSOLVENTE'
);


ALTER TYPE school.estado_solvencia OWNER TO postgres;

--
-- TOC entry 959 (class 1247 OID 24698)
-- Name: estado_usuario; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.estado_usuario AS ENUM (
    'ACTIVO',
    'INACTIVO',
    'BLOQUEADO'
);


ALTER TYPE school.estado_usuario OWNER TO postgres;

--
-- TOC entry 941 (class 1247 OID 24642)
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
-- TOC entry 926 (class 1247 OID 24598)
-- Name: tipo_inscripcion; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.tipo_inscripcion AS ENUM (
    'NUEVA',
    'REINSCRIPCION',
    'TRASLADO'
);


ALTER TYPE school.tipo_inscripcion OWNER TO postgres;

--
-- TOC entry 950 (class 1247 OID 24670)
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
-- TOC entry 932 (class 1247 OID 24616)
-- Name: tipo_precio; Type: TYPE; Schema: school; Owner: postgres
--

CREATE TYPE school.tipo_precio AS ENUM (
    'INSCRIPCION',
    'MENSUALIDAD',
    'OTRO'
);


ALTER TYPE school.tipo_precio OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 245 (class 1259 OID 24996)
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
-- TOC entry 244 (class 1259 OID 24995)
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
-- TOC entry 5560 (class 0 OID 0)
-- Dependencies: 244
-- Name: aplicacion_pago_id_aplicacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.aplicacion_pago_id_aplicacion_seq OWNED BY school.aplicacion_pago.id_aplicacion;


--
-- TOC entry 281 (class 1259 OID 25410)
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
-- TOC entry 280 (class 1259 OID 25409)
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
-- TOC entry 5561 (class 0 OID 0)
-- Dependencies: 280
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.auditoria_id_auditoria_seq OWNED BY school.auditoria.id_auditoria;


--
-- TOC entry 249 (class 1259 OID 25046)
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
-- TOC entry 251 (class 1259 OID 25064)
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
-- TOC entry 250 (class 1259 OID 25063)
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
-- TOC entry 5562 (class 0 OID 0)
-- Dependencies: 250
-- Name: beca_estudiante_id_beca_estudiante_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.beca_estudiante_id_beca_estudiante_seq OWNED BY school.beca_estudiante.id_beca_estudiante;


--
-- TOC entry 248 (class 1259 OID 25045)
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
-- TOC entry 5563 (class 0 OID 0)
-- Dependencies: 248
-- Name: beca_id_beca_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.beca_id_beca_seq OWNED BY school.beca.id_beca;


--
-- TOC entry 257 (class 1259 OID 25130)
-- Name: cambio_carrera; Type: TABLE; Schema: school; Owner: postgres
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


ALTER TABLE school.cambio_carrera OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 25129)
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
-- TOC entry 5564 (class 0 OID 0)
-- Dependencies: 256
-- Name: cambio_carrera_id_cambio_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.cambio_carrera_id_cambio_seq OWNED BY school.cambio_carrera.id_cambio;


--
-- TOC entry 223 (class 1259 OID 24724)
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
-- TOC entry 225 (class 1259 OID 24741)
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
-- TOC entry 224 (class 1259 OID 24740)
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
-- TOC entry 5565 (class 0 OID 0)
-- Dependencies: 224
-- Name: carrera_ciclo_id_carrera_ciclo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.carrera_ciclo_id_carrera_ciclo_seq OWNED BY school.carrera_ciclo.id_carrera_ciclo;


--
-- TOC entry 222 (class 1259 OID 24723)
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
-- TOC entry 5566 (class 0 OID 0)
-- Dependencies: 222
-- Name: carrera_id_carrera_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.carrera_id_carrera_seq OWNED BY school.carrera.id_carrera;


--
-- TOC entry 221 (class 1259 OID 24706)
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
-- TOC entry 220 (class 1259 OID 24705)
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
-- TOC entry 5567 (class 0 OID 0)
-- Dependencies: 220
-- Name: ciclo_escolar_id_ciclo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.ciclo_escolar_id_ciclo_seq OWNED BY school.ciclo_escolar.id_ciclo;


--
-- TOC entry 265 (class 1259 OID 25250)
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
-- TOC entry 264 (class 1259 OID 25249)
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
-- TOC entry 5568 (class 0 OID 0)
-- Dependencies: 264
-- Name: contacto_id_contacto_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.contacto_id_contacto_seq OWNED BY school.contacto.id_contacto;


--
-- TOC entry 253 (class 1259 OID 25088)
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
-- TOC entry 252 (class 1259 OID 25087)
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
-- TOC entry 5569 (class 0 OID 0)
-- Dependencies: 252
-- Name: descuento_id_descuento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.descuento_id_descuento_seq OWNED BY school.descuento.id_descuento;


--
-- TOC entry 255 (class 1259 OID 25106)
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
-- TOC entry 254 (class 1259 OID 25105)
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
-- TOC entry 5570 (class 0 OID 0)
-- Dependencies: 254
-- Name: descuento_obligacion_id_descuento_obligacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.descuento_obligacion_id_descuento_obligacion_seq OWNED BY school.descuento_obligacion.id_descuento_obligacion;


--
-- TOC entry 237 (class 1259 OID 24885)
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
-- TOC entry 236 (class 1259 OID 24884)
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
-- TOC entry 5571 (class 0 OID 0)
-- Dependencies: 236
-- Name: documento_expediente_id_documento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.documento_expediente_id_documento_seq OWNED BY school.documento_expediente.id_documento;


--
-- TOC entry 271 (class 1259 OID 25309)
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
-- TOC entry 270 (class 1259 OID 25308)
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
-- TOC entry 5572 (class 0 OID 0)
-- Dependencies: 270
-- Name: empleado_id_empleado_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.empleado_id_empleado_seq OWNED BY school.empleado.id_empleado;


--
-- TOC entry 229 (class 1259 OID 24787)
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
-- TOC entry 228 (class 1259 OID 24786)
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
-- TOC entry 5573 (class 0 OID 0)
-- Dependencies: 228
-- Name: estudiante_id_estudiante_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.estudiante_id_estudiante_seq OWNED BY school.estudiante.id_estudiante;


--
-- TOC entry 261 (class 1259 OID 25194)
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
-- TOC entry 260 (class 1259 OID 25193)
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
-- TOC entry 5574 (class 0 OID 0)
-- Dependencies: 260
-- Name: evaluacion_id_evaluacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.evaluacion_id_evaluacion_seq OWNED BY school.evaluacion.id_evaluacion;


--
-- TOC entry 233 (class 1259 OID 24846)
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
-- TOC entry 232 (class 1259 OID 24845)
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
-- TOC entry 5575 (class 0 OID 0)
-- Dependencies: 232
-- Name: expediente_id_expediente_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.expediente_id_expediente_seq OWNED BY school.expediente.id_expediente;


--
-- TOC entry 227 (class 1259 OID 24767)
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
-- TOC entry 226 (class 1259 OID 24766)
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
-- TOC entry 5576 (class 0 OID 0)
-- Dependencies: 226
-- Name: grado_id_grado_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.grado_id_grado_seq OWNED BY school.grado.id_grado;


--
-- TOC entry 231 (class 1259 OID 24810)
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
-- TOC entry 230 (class 1259 OID 24809)
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
-- TOC entry 5577 (class 0 OID 0)
-- Dependencies: 230
-- Name: inscripcion_id_inscripcion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.inscripcion_id_inscripcion_seq OWNED BY school.inscripcion.id_inscripcion;


--
-- TOC entry 259 (class 1259 OID 25161)
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
-- TOC entry 258 (class 1259 OID 25160)
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
-- TOC entry 5578 (class 0 OID 0)
-- Dependencies: 258
-- Name: movimiento_saldo_id_movimiento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.movimiento_saldo_id_movimiento_seq OWNED BY school.movimiento_saldo.id_movimiento;


--
-- TOC entry 267 (class 1259 OID 25269)
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
-- TOC entry 269 (class 1259 OID 25284)
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
-- TOC entry 268 (class 1259 OID 25283)
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
-- TOC entry 5579 (class 0 OID 0)
-- Dependencies: 268
-- Name: notificacion_destinatario_id_destinatario_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.notificacion_destinatario_id_destinatario_seq OWNED BY school.notificacion_destinatario.id_destinatario;


--
-- TOC entry 266 (class 1259 OID 25268)
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
-- TOC entry 5580 (class 0 OID 0)
-- Dependencies: 266
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.notificacion_id_notificacion_seq OWNED BY school.notificacion.id_notificacion;


--
-- TOC entry 241 (class 1259 OID 24935)
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
    monto_descuento numeric(12,2) DEFAULT 0 NOT NULL,
    monto_beca numeric(12,2) DEFAULT 0 NOT NULL,
    monto_neto numeric(12,2) NOT NULL,
    estado school.estado_obligacion DEFAULT 'PENDIENTE'::school.estado_obligacion NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_obligacion_beca CHECK ((monto_beca >= (0)::numeric)),
    CONSTRAINT ck_obligacion_bruto CHECK ((monto_bruto >= (0)::numeric)),
    CONSTRAINT ck_obligacion_descuento CHECK ((monto_descuento >= (0)::numeric)),
    CONSTRAINT ck_obligacion_descuentos CHECK (((monto_descuento + monto_beca) <= monto_bruto)),
    CONSTRAINT ck_obligacion_neto CHECK ((monto_neto >= (0)::numeric))
);


ALTER TABLE school.obligacion OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 24934)
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
-- TOC entry 5581 (class 0 OID 0)
-- Dependencies: 240
-- Name: obligacion_id_obligacion_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.obligacion_id_obligacion_seq OWNED BY school.obligacion.id_obligacion;


--
-- TOC entry 243 (class 1259 OID 24970)
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
-- TOC entry 242 (class 1259 OID 24969)
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
-- TOC entry 5582 (class 0 OID 0)
-- Dependencies: 242
-- Name: pago_id_pago_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.pago_id_pago_seq OWNED BY school.pago.id_pago;


--
-- TOC entry 277 (class 1259 OID 25363)
-- Name: permiso; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.permiso (
    id_permiso bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text
);


ALTER TABLE school.permiso OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 25362)
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
-- TOC entry 5583 (class 0 OID 0)
-- Dependencies: 276
-- Name: permiso_id_permiso_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.permiso_id_permiso_seq OWNED BY school.permiso.id_permiso;


--
-- TOC entry 239 (class 1259 OID 24911)
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
-- TOC entry 238 (class 1259 OID 24910)
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
-- TOC entry 5584 (class 0 OID 0)
-- Dependencies: 238
-- Name: precio_carrera_id_precio_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.precio_carrera_id_precio_seq OWNED BY school.precio_carrera.id_precio;


--
-- TOC entry 247 (class 1259 OID 25022)
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
-- TOC entry 246 (class 1259 OID 25021)
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
-- TOC entry 5585 (class 0 OID 0)
-- Dependencies: 246
-- Name: recibo_id_recibo_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.recibo_id_recibo_seq OWNED BY school.recibo.id_recibo;


--
-- TOC entry 275 (class 1259 OID 25348)
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
-- TOC entry 274 (class 1259 OID 25347)
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
-- TOC entry 5586 (class 0 OID 0)
-- Dependencies: 274
-- Name: rol_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.rol_id_rol_seq OWNED BY school.rol.id_rol;


--
-- TOC entry 279 (class 1259 OID 25392)
-- Name: rol_permiso; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.rol_permiso (
    id_rol bigint NOT NULL,
    id_permiso bigint NOT NULL
);


ALTER TABLE school.rol_permiso OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 25213)
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
-- TOC entry 262 (class 1259 OID 25212)
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
-- TOC entry 5587 (class 0 OID 0)
-- Dependencies: 262
-- Name: solvencia_id_solvencia_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.solvencia_id_solvencia_seq OWNED BY school.solvencia.id_solvencia;


--
-- TOC entry 235 (class 1259 OID 24868)
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
-- TOC entry 234 (class 1259 OID 24867)
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
-- TOC entry 5588 (class 0 OID 0)
-- Dependencies: 234
-- Name: tipo_documento_id_tipo_documento_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.tipo_documento_id_tipo_documento_seq OWNED BY school.tipo_documento.id_tipo_documento;


--
-- TOC entry 273 (class 1259 OID 25323)
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
-- TOC entry 272 (class 1259 OID 25322)
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
-- TOC entry 5589 (class 0 OID 0)
-- Dependencies: 272
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: school; Owner: postgres
--

ALTER SEQUENCE school.usuario_id_usuario_seq OWNED BY school.usuario.id_usuario;


--
-- TOC entry 278 (class 1259 OID 25375)
-- Name: usuario_rol; Type: TABLE; Schema: school; Owner: postgres
--

CREATE TABLE school.usuario_rol (
    id_usuario bigint NOT NULL,
    id_rol bigint NOT NULL
);


ALTER TABLE school.usuario_rol OWNER TO postgres;

--
-- TOC entry 282 (class 1259 OID 25447)
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
-- TOC entry 286 (class 1259 OID 25467)
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
-- TOC entry 287 (class 1259 OID 25472)
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
-- TOC entry 285 (class 1259 OID 25462)
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
-- TOC entry 284 (class 1259 OID 25457)
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
-- TOC entry 283 (class 1259 OID 25452)
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
-- TOC entry 5117 (class 2604 OID 24999)
-- Name: aplicacion_pago id_aplicacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago ALTER COLUMN id_aplicacion SET DEFAULT nextval('school.aplicacion_pago_id_aplicacion_seq'::regclass);


--
-- TOC entry 5155 (class 2604 OID 25413)
-- Name: auditoria id_auditoria; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.auditoria ALTER COLUMN id_auditoria SET DEFAULT nextval('school.auditoria_id_auditoria_seq'::regclass);


--
-- TOC entry 5121 (class 2604 OID 25049)
-- Name: beca id_beca; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca ALTER COLUMN id_beca SET DEFAULT nextval('school.beca_id_beca_seq'::regclass);


--
-- TOC entry 5123 (class 2604 OID 25067)
-- Name: beca_estudiante id_beca_estudiante; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante ALTER COLUMN id_beca_estudiante SET DEFAULT nextval('school.beca_estudiante_id_beca_estudiante_seq'::regclass);


--
-- TOC entry 5128 (class 2604 OID 25133)
-- Name: cambio_carrera id_cambio; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera ALTER COLUMN id_cambio SET DEFAULT nextval('school.cambio_carrera_id_cambio_seq'::regclass);


--
-- TOC entry 5079 (class 2604 OID 24727)
-- Name: carrera id_carrera; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera ALTER COLUMN id_carrera SET DEFAULT nextval('school.carrera_id_carrera_seq'::regclass);


--
-- TOC entry 5082 (class 2604 OID 24744)
-- Name: carrera_ciclo id_carrera_ciclo; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo ALTER COLUMN id_carrera_ciclo SET DEFAULT nextval('school.carrera_ciclo_id_carrera_ciclo_seq'::regclass);


--
-- TOC entry 5076 (class 2604 OID 24709)
-- Name: ciclo_escolar id_ciclo; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.ciclo_escolar ALTER COLUMN id_ciclo SET DEFAULT nextval('school.ciclo_escolar_id_ciclo_seq'::regclass);


--
-- TOC entry 5138 (class 2604 OID 25253)
-- Name: contacto id_contacto; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.contacto ALTER COLUMN id_contacto SET DEFAULT nextval('school.contacto_id_contacto_seq'::regclass);


--
-- TOC entry 5124 (class 2604 OID 25091)
-- Name: descuento id_descuento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento ALTER COLUMN id_descuento SET DEFAULT nextval('school.descuento_id_descuento_seq'::regclass);


--
-- TOC entry 5126 (class 2604 OID 25109)
-- Name: descuento_obligacion id_descuento_obligacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion ALTER COLUMN id_descuento_obligacion SET DEFAULT nextval('school.descuento_obligacion_id_descuento_obligacion_seq'::regclass);


--
-- TOC entry 5102 (class 2604 OID 24888)
-- Name: documento_expediente id_documento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente ALTER COLUMN id_documento SET DEFAULT nextval('school.documento_expediente_id_documento_seq'::regclass);


--
-- TOC entry 5146 (class 2604 OID 25312)
-- Name: empleado id_empleado; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.empleado ALTER COLUMN id_empleado SET DEFAULT nextval('school.empleado_id_empleado_seq'::regclass);


--
-- TOC entry 5087 (class 2604 OID 24790)
-- Name: estudiante id_estudiante; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante ALTER COLUMN id_estudiante SET DEFAULT nextval('school.estudiante_id_estudiante_seq'::regclass);


--
-- TOC entry 5134 (class 2604 OID 25197)
-- Name: evaluacion id_evaluacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.evaluacion ALTER COLUMN id_evaluacion SET DEFAULT nextval('school.evaluacion_id_evaluacion_seq'::regclass);


--
-- TOC entry 5096 (class 2604 OID 24849)
-- Name: expediente id_expediente; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente ALTER COLUMN id_expediente SET DEFAULT nextval('school.expediente_id_expediente_seq'::regclass);


--
-- TOC entry 5085 (class 2604 OID 24770)
-- Name: grado id_grado; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado ALTER COLUMN id_grado SET DEFAULT nextval('school.grado_id_grado_seq'::regclass);


--
-- TOC entry 5091 (class 2604 OID 24813)
-- Name: inscripcion id_inscripcion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion ALTER COLUMN id_inscripcion SET DEFAULT nextval('school.inscripcion_id_inscripcion_seq'::regclass);


--
-- TOC entry 5131 (class 2604 OID 25164)
-- Name: movimiento_saldo id_movimiento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo ALTER COLUMN id_movimiento SET DEFAULT nextval('school.movimiento_saldo_id_movimiento_seq'::regclass);


--
-- TOC entry 5141 (class 2604 OID 25272)
-- Name: notificacion id_notificacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion ALTER COLUMN id_notificacion SET DEFAULT nextval('school.notificacion_id_notificacion_seq'::regclass);


--
-- TOC entry 5143 (class 2604 OID 25287)
-- Name: notificacion_destinatario id_destinatario; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario ALTER COLUMN id_destinatario SET DEFAULT nextval('school.notificacion_destinatario_id_destinatario_seq'::regclass);


--
-- TOC entry 5108 (class 2604 OID 24938)
-- Name: obligacion id_obligacion; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion ALTER COLUMN id_obligacion SET DEFAULT nextval('school.obligacion_id_obligacion_seq'::regclass);


--
-- TOC entry 5113 (class 2604 OID 24973)
-- Name: pago id_pago; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.pago ALTER COLUMN id_pago SET DEFAULT nextval('school.pago_id_pago_seq'::regclass);


--
-- TOC entry 5154 (class 2604 OID 25366)
-- Name: permiso id_permiso; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.permiso ALTER COLUMN id_permiso SET DEFAULT nextval('school.permiso_id_permiso_seq'::regclass);


--
-- TOC entry 5105 (class 2604 OID 24914)
-- Name: precio_carrera id_precio; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.precio_carrera ALTER COLUMN id_precio SET DEFAULT nextval('school.precio_carrera_id_precio_seq'::regclass);


--
-- TOC entry 5119 (class 2604 OID 25025)
-- Name: recibo id_recibo; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo ALTER COLUMN id_recibo SET DEFAULT nextval('school.recibo_id_recibo_seq'::regclass);


--
-- TOC entry 5152 (class 2604 OID 25351)
-- Name: rol id_rol; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol ALTER COLUMN id_rol SET DEFAULT nextval('school.rol_id_rol_seq'::regclass);


--
-- TOC entry 5136 (class 2604 OID 25216)
-- Name: solvencia id_solvencia; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia ALTER COLUMN id_solvencia SET DEFAULT nextval('school.solvencia_id_solvencia_seq'::regclass);


--
-- TOC entry 5099 (class 2604 OID 24871)
-- Name: tipo_documento id_tipo_documento; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.tipo_documento ALTER COLUMN id_tipo_documento SET DEFAULT nextval('school.tipo_documento_id_tipo_documento_seq'::regclass);


--
-- TOC entry 5149 (class 2604 OID 25326)
-- Name: usuario id_usuario; Type: DEFAULT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('school.usuario_id_usuario_seq'::regclass);


--
-- TOC entry 5518 (class 0 OID 24996)
-- Dependencies: 245
-- Data for Name: aplicacion_pago; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.aplicacion_pago (id_aplicacion, id_pago, id_obligacion, monto_aplicado, fecha_aplicacion) FROM stdin;
\.


--
-- TOC entry 5554 (class 0 OID 25410)
-- Dependencies: 281
-- Data for Name: auditoria; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.auditoria (id_auditoria, id_usuario, fecha_evento, modulo, accion, tabla_afectada, id_registro, descripcion, datos_anteriores, datos_nuevos, ip) FROM stdin;
\.


--
-- TOC entry 5522 (class 0 OID 25046)
-- Dependencies: 249
-- Data for Name: beca; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.beca (id_beca, nombre, descripcion, porcentaje, convenio, estado, fecha_inicio, fecha_fin) FROM stdin;
\.


--
-- TOC entry 5524 (class 0 OID 25064)
-- Dependencies: 251
-- Data for Name: beca_estudiante; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.beca_estudiante (id_beca_estudiante, id_beca, id_estudiante, fecha_inicio, fecha_fin, porcentaje_aplicado, observaciones) FROM stdin;
\.


--
-- TOC entry 5530 (class 0 OID 25130)
-- Dependencies: 257
-- Data for Name: cambio_carrera; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.cambio_carrera (id_cambio, id_estudiante, id_inscripcion_origen, id_inscripcion_destino, fecha_solicitud, fecha_aprobacion, motivo, estado, id_usuario, observaciones) FROM stdin;
\.


--
-- TOC entry 5496 (class 0 OID 24724)
-- Dependencies: 223
-- Data for Name: carrera; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.carrera (id_carrera, nombre, descripcion, activo, creado_en) FROM stdin;
\.


--
-- TOC entry 5498 (class 0 OID 24741)
-- Dependencies: 225
-- Data for Name: carrera_ciclo; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.carrera_ciclo (id_carrera_ciclo, id_carrera, id_ciclo, nombre_comercial, estado, creado_en) FROM stdin;
\.


--
-- TOC entry 5494 (class 0 OID 24706)
-- Dependencies: 221
-- Data for Name: ciclo_escolar; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.ciclo_escolar (id_ciclo, nombre, fecha_inicio, fecha_fin, estado, creado_en) FROM stdin;
\.


--
-- TOC entry 5538 (class 0 OID 25250)
-- Dependencies: 265
-- Data for Name: contacto; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.contacto (id_contacto, id_estudiante, nombre, parentesco, telefono, whatsapp, email, es_principal, activo) FROM stdin;
\.


--
-- TOC entry 5526 (class 0 OID 25088)
-- Dependencies: 253
-- Data for Name: descuento; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.descuento (id_descuento, nombre, descripcion, porcentaje, monto_fijo, activo) FROM stdin;
\.


--
-- TOC entry 5528 (class 0 OID 25106)
-- Dependencies: 255
-- Data for Name: descuento_obligacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.descuento_obligacion (id_descuento_obligacion, id_descuento, id_obligacion, monto_aplicado, fecha_aplicacion) FROM stdin;
\.


--
-- TOC entry 5510 (class 0 OID 24885)
-- Dependencies: 237
-- Data for Name: documento_expediente; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.documento_expediente (id_documento, id_expediente, id_tipo_documento, nombre_archivo, ruta_archivo, fecha_entrega, entregado, observaciones, creado_en) FROM stdin;
\.


--
-- TOC entry 5544 (class 0 OID 25309)
-- Dependencies: 271
-- Data for Name: empleado; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.empleado (id_empleado, nombres, apellidos, telefono, email, cargo, activo, creado_en) FROM stdin;
\.


--
-- TOC entry 5502 (class 0 OID 24787)
-- Dependencies: 229
-- Data for Name: estudiante; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.estudiante (id_estudiante, codigo_estudiante, cui, nombres, apellidos, fecha_nacimiento, telefono, whatsapp, email, direccion, estado, creado_en, actualizado_en) FROM stdin;
\.


--
-- TOC entry 5534 (class 0 OID 25194)
-- Dependencies: 261
-- Data for Name: evaluacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.evaluacion (id_evaluacion, id_ciclo, nombre, fecha_evaluacion, fecha_corte_finanzas, activo) FROM stdin;
\.


--
-- TOC entry 5506 (class 0 OID 24846)
-- Dependencies: 233
-- Data for Name: expediente; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.expediente (id_expediente, id_estudiante, observaciones, creado_en, actualizado_en) FROM stdin;
\.


--
-- TOC entry 5500 (class 0 OID 24767)
-- Dependencies: 227
-- Data for Name: grado; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.grado (id_grado, id_carrera_ciclo, nombre, nivel_orden, activo) FROM stdin;
\.


--
-- TOC entry 5504 (class 0 OID 24810)
-- Dependencies: 231
-- Data for Name: inscripcion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.inscripcion (id_inscripcion, id_estudiante, id_carrera_ciclo, id_grado, fecha_inscripcion, tipo, estado, observaciones, creado_en) FROM stdin;
\.


--
-- TOC entry 5532 (class 0 OID 25161)
-- Dependencies: 259
-- Data for Name: movimiento_saldo; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.movimiento_saldo (id_movimiento, id_estudiante, id_inscripcion_origen, id_inscripcion_destino, tipo, monto, fecha_movimiento, motivo, estado, id_usuario, referencia) FROM stdin;
\.


--
-- TOC entry 5540 (class 0 OID 25269)
-- Dependencies: 267
-- Data for Name: notificacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.notificacion (id_notificacion, titulo, mensaje, fecha_creacion, id_usuario) FROM stdin;
\.


--
-- TOC entry 5542 (class 0 OID 25284)
-- Dependencies: 269
-- Data for Name: notificacion_destinatario; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.notificacion_destinatario (id_destinatario, id_notificacion, id_contacto, estado, fecha_generado, fecha_abierto) FROM stdin;
\.


--
-- TOC entry 5514 (class 0 OID 24935)
-- Dependencies: 241
-- Data for Name: obligacion; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.obligacion (id_obligacion, id_inscripcion, id_precio, concepto, periodo, fecha_vencimiento, monto_bruto, monto_descuento, monto_beca, monto_neto, estado, creado_en) FROM stdin;
\.


--
-- TOC entry 5516 (class 0 OID 24970)
-- Dependencies: 243
-- Data for Name: pago; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.pago (id_pago, id_estudiante, id_usuario, fecha_pago, monto_total, metodo, referencia, observaciones, estado, creado_en) FROM stdin;
\.


--
-- TOC entry 5550 (class 0 OID 25363)
-- Dependencies: 277
-- Data for Name: permiso; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.permiso (id_permiso, nombre, descripcion) FROM stdin;
\.


--
-- TOC entry 5512 (class 0 OID 24911)
-- Dependencies: 239
-- Data for Name: precio_carrera; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.precio_carrera (id_precio, id_carrera_ciclo, tipo, concepto, monto, fecha_inicio, fecha_fin, activo, creado_en) FROM stdin;
\.


--
-- TOC entry 5520 (class 0 OID 25022)
-- Dependencies: 247
-- Data for Name: recibo; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.recibo (id_recibo, id_pago, numero_recibo, codigo_verificacion, fecha_emision) FROM stdin;
\.


--
-- TOC entry 5548 (class 0 OID 25348)
-- Dependencies: 275
-- Data for Name: rol; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.rol (id_rol, nombre, descripcion, activo) FROM stdin;
\.


--
-- TOC entry 5552 (class 0 OID 25392)
-- Dependencies: 279
-- Data for Name: rol_permiso; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.rol_permiso (id_rol, id_permiso) FROM stdin;
\.


--
-- TOC entry 5536 (class 0 OID 25213)
-- Dependencies: 263
-- Data for Name: solvencia; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.solvencia (id_solvencia, id_estudiante, id_inscripcion, id_evaluacion, fecha_generacion, fecha_corte, saldo_corte, estado, codigo_verificacion, observaciones) FROM stdin;
\.


--
-- TOC entry 5508 (class 0 OID 24868)
-- Dependencies: 235
-- Data for Name: tipo_documento; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.tipo_documento (id_tipo_documento, nombre, descripcion, obligatorio, activo) FROM stdin;
\.


--
-- TOC entry 5546 (class 0 OID 25323)
-- Dependencies: 273
-- Data for Name: usuario; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.usuario (id_usuario, id_empleado, username, password_hash, estado, ultimo_acceso, creado_en) FROM stdin;
\.


--
-- TOC entry 5551 (class 0 OID 25375)
-- Dependencies: 278
-- Data for Name: usuario_rol; Type: TABLE DATA; Schema: school; Owner: postgres
--

COPY school.usuario_rol (id_usuario, id_rol) FROM stdin;
\.


--
-- TOC entry 5590 (class 0 OID 0)
-- Dependencies: 244
-- Name: aplicacion_pago_id_aplicacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.aplicacion_pago_id_aplicacion_seq', 1, false);


--
-- TOC entry 5591 (class 0 OID 0)
-- Dependencies: 280
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.auditoria_id_auditoria_seq', 1, false);


--
-- TOC entry 5592 (class 0 OID 0)
-- Dependencies: 250
-- Name: beca_estudiante_id_beca_estudiante_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.beca_estudiante_id_beca_estudiante_seq', 1, false);


--
-- TOC entry 5593 (class 0 OID 0)
-- Dependencies: 248
-- Name: beca_id_beca_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.beca_id_beca_seq', 1, false);


--
-- TOC entry 5594 (class 0 OID 0)
-- Dependencies: 256
-- Name: cambio_carrera_id_cambio_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.cambio_carrera_id_cambio_seq', 1, false);


--
-- TOC entry 5595 (class 0 OID 0)
-- Dependencies: 224
-- Name: carrera_ciclo_id_carrera_ciclo_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.carrera_ciclo_id_carrera_ciclo_seq', 1, false);


--
-- TOC entry 5596 (class 0 OID 0)
-- Dependencies: 222
-- Name: carrera_id_carrera_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.carrera_id_carrera_seq', 1, false);


--
-- TOC entry 5597 (class 0 OID 0)
-- Dependencies: 220
-- Name: ciclo_escolar_id_ciclo_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.ciclo_escolar_id_ciclo_seq', 1, false);


--
-- TOC entry 5598 (class 0 OID 0)
-- Dependencies: 264
-- Name: contacto_id_contacto_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.contacto_id_contacto_seq', 1, false);


--
-- TOC entry 5599 (class 0 OID 0)
-- Dependencies: 252
-- Name: descuento_id_descuento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.descuento_id_descuento_seq', 1, false);


--
-- TOC entry 5600 (class 0 OID 0)
-- Dependencies: 254
-- Name: descuento_obligacion_id_descuento_obligacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.descuento_obligacion_id_descuento_obligacion_seq', 1, false);


--
-- TOC entry 5601 (class 0 OID 0)
-- Dependencies: 236
-- Name: documento_expediente_id_documento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.documento_expediente_id_documento_seq', 1, false);


--
-- TOC entry 5602 (class 0 OID 0)
-- Dependencies: 270
-- Name: empleado_id_empleado_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.empleado_id_empleado_seq', 1, false);


--
-- TOC entry 5603 (class 0 OID 0)
-- Dependencies: 228
-- Name: estudiante_id_estudiante_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.estudiante_id_estudiante_seq', 1, false);


--
-- TOC entry 5604 (class 0 OID 0)
-- Dependencies: 260
-- Name: evaluacion_id_evaluacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.evaluacion_id_evaluacion_seq', 1, false);


--
-- TOC entry 5605 (class 0 OID 0)
-- Dependencies: 232
-- Name: expediente_id_expediente_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.expediente_id_expediente_seq', 1, false);


--
-- TOC entry 5606 (class 0 OID 0)
-- Dependencies: 226
-- Name: grado_id_grado_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.grado_id_grado_seq', 1, false);


--
-- TOC entry 5607 (class 0 OID 0)
-- Dependencies: 230
-- Name: inscripcion_id_inscripcion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.inscripcion_id_inscripcion_seq', 1, false);


--
-- TOC entry 5608 (class 0 OID 0)
-- Dependencies: 258
-- Name: movimiento_saldo_id_movimiento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.movimiento_saldo_id_movimiento_seq', 1, false);


--
-- TOC entry 5609 (class 0 OID 0)
-- Dependencies: 268
-- Name: notificacion_destinatario_id_destinatario_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.notificacion_destinatario_id_destinatario_seq', 1, false);


--
-- TOC entry 5610 (class 0 OID 0)
-- Dependencies: 266
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.notificacion_id_notificacion_seq', 1, false);


--
-- TOC entry 5611 (class 0 OID 0)
-- Dependencies: 240
-- Name: obligacion_id_obligacion_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.obligacion_id_obligacion_seq', 1, false);


--
-- TOC entry 5612 (class 0 OID 0)
-- Dependencies: 242
-- Name: pago_id_pago_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.pago_id_pago_seq', 1, false);


--
-- TOC entry 5613 (class 0 OID 0)
-- Dependencies: 276
-- Name: permiso_id_permiso_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.permiso_id_permiso_seq', 1, false);


--
-- TOC entry 5614 (class 0 OID 0)
-- Dependencies: 238
-- Name: precio_carrera_id_precio_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.precio_carrera_id_precio_seq', 1, false);


--
-- TOC entry 5615 (class 0 OID 0)
-- Dependencies: 246
-- Name: recibo_id_recibo_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.recibo_id_recibo_seq', 1, false);


--
-- TOC entry 5616 (class 0 OID 0)
-- Dependencies: 274
-- Name: rol_id_rol_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.rol_id_rol_seq', 1, false);


--
-- TOC entry 5617 (class 0 OID 0)
-- Dependencies: 262
-- Name: solvencia_id_solvencia_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.solvencia_id_solvencia_seq', 1, false);


--
-- TOC entry 5618 (class 0 OID 0)
-- Dependencies: 234
-- Name: tipo_documento_id_tipo_documento_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.tipo_documento_id_tipo_documento_seq', 1, false);


--
-- TOC entry 5619 (class 0 OID 0)
-- Dependencies: 272
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: school; Owner: postgres
--

SELECT pg_catalog.setval('school.usuario_id_usuario_seq', 1, false);


--
-- TOC entry 5230 (class 2606 OID 25008)
-- Name: aplicacion_pago aplicacion_pago_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT aplicacion_pago_pkey PRIMARY KEY (id_aplicacion);


--
-- TOC entry 5298 (class 2606 OID 25420)
-- Name: auditoria auditoria_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id_auditoria);


--
-- TOC entry 5248 (class 2606 OID 25076)
-- Name: beca_estudiante beca_estudiante_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT beca_estudiante_pkey PRIMARY KEY (id_beca_estudiante);


--
-- TOC entry 5244 (class 2606 OID 25060)
-- Name: beca beca_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca
    ADD CONSTRAINT beca_pkey PRIMARY KEY (id_beca);


--
-- TOC entry 5256 (class 2606 OID 25144)
-- Name: cambio_carrera cambio_carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT cambio_carrera_pkey PRIMARY KEY (id_cambio);


--
-- TOC entry 5187 (class 2606 OID 24753)
-- Name: carrera_ciclo carrera_ciclo_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT carrera_ciclo_pkey PRIMARY KEY (id_carrera_ciclo);


--
-- TOC entry 5183 (class 2606 OID 24737)
-- Name: carrera carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera
    ADD CONSTRAINT carrera_pkey PRIMARY KEY (id_carrera);


--
-- TOC entry 5179 (class 2606 OID 24720)
-- Name: ciclo_escolar ciclo_escolar_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.ciclo_escolar
    ADD CONSTRAINT ciclo_escolar_pkey PRIMARY KEY (id_ciclo);


--
-- TOC entry 5271 (class 2606 OID 25262)
-- Name: contacto contacto_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.contacto
    ADD CONSTRAINT contacto_pkey PRIMARY KEY (id_contacto);


--
-- TOC entry 5254 (class 2606 OID 25118)
-- Name: descuento_obligacion descuento_obligacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT descuento_obligacion_pkey PRIMARY KEY (id_descuento_obligacion);


--
-- TOC entry 5250 (class 2606 OID 25102)
-- Name: descuento descuento_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento
    ADD CONSTRAINT descuento_pkey PRIMARY KEY (id_descuento);


--
-- TOC entry 5216 (class 2606 OID 24899)
-- Name: documento_expediente documento_expediente_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT documento_expediente_pkey PRIMARY KEY (id_documento);


--
-- TOC entry 5278 (class 2606 OID 25321)
-- Name: empleado empleado_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.empleado
    ADD CONSTRAINT empleado_pkey PRIMARY KEY (id_empleado);


--
-- TOC entry 5195 (class 2606 OID 24804)
-- Name: estudiante estudiante_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT estudiante_pkey PRIMARY KEY (id_estudiante);


--
-- TOC entry 5263 (class 2606 OID 25206)
-- Name: evaluacion evaluacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.evaluacion
    ADD CONSTRAINT evaluacion_pkey PRIMARY KEY (id_evaluacion);


--
-- TOC entry 5208 (class 2606 OID 24859)
-- Name: expediente expediente_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT expediente_pkey PRIMARY KEY (id_expediente);


--
-- TOC entry 5191 (class 2606 OID 24778)
-- Name: grado grado_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT grado_pkey PRIMARY KEY (id_grado);


--
-- TOC entry 5206 (class 2606 OID 24829)
-- Name: inscripcion inscripcion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT inscripcion_pkey PRIMARY KEY (id_inscripcion);


--
-- TOC entry 5261 (class 2606 OID 25177)
-- Name: movimiento_saldo movimiento_saldo_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT movimiento_saldo_pkey PRIMARY KEY (id_movimiento);


--
-- TOC entry 5276 (class 2606 OID 25296)
-- Name: notificacion_destinatario notificacion_destinatario_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT notificacion_destinatario_pkey PRIMARY KEY (id_destinatario);


--
-- TOC entry 5274 (class 2606 OID 25282)
-- Name: notificacion notificacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion
    ADD CONSTRAINT notificacion_pkey PRIMARY KEY (id_notificacion);


--
-- TOC entry 5224 (class 2606 OID 24958)
-- Name: obligacion obligacion_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT obligacion_pkey PRIMARY KEY (id_obligacion);


--
-- TOC entry 5228 (class 2606 OID 24988)
-- Name: pago pago_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.pago
    ADD CONSTRAINT pago_pkey PRIMARY KEY (id_pago);


--
-- TOC entry 5290 (class 2606 OID 25372)
-- Name: permiso permiso_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.permiso
    ADD CONSTRAINT permiso_pkey PRIMARY KEY (id_permiso);


--
-- TOC entry 5219 (class 2606 OID 24928)
-- Name: precio_carrera precio_carrera_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.precio_carrera
    ADD CONSTRAINT precio_carrera_pkey PRIMARY KEY (id_precio);


--
-- TOC entry 5236 (class 2606 OID 25033)
-- Name: recibo recibo_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT recibo_pkey PRIMARY KEY (id_recibo);


--
-- TOC entry 5296 (class 2606 OID 25398)
-- Name: rol_permiso rol_permiso_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT rol_permiso_pkey PRIMARY KEY (id_rol, id_permiso);


--
-- TOC entry 5286 (class 2606 OID 25359)
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- TOC entry 5267 (class 2606 OID 25231)
-- Name: solvencia solvencia_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT solvencia_pkey PRIMARY KEY (id_solvencia);


--
-- TOC entry 5212 (class 2606 OID 24881)
-- Name: tipo_documento tipo_documento_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.tipo_documento
    ADD CONSTRAINT tipo_documento_pkey PRIMARY KEY (id_tipo_documento);


--
-- TOC entry 5234 (class 2606 OID 25010)
-- Name: aplicacion_pago uq_aplicacion_pago_obligacion; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT uq_aplicacion_pago_obligacion UNIQUE (id_pago, id_obligacion);


--
-- TOC entry 5246 (class 2606 OID 25062)
-- Name: beca uq_beca_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca
    ADD CONSTRAINT uq_beca_nombre UNIQUE (nombre);


--
-- TOC entry 5189 (class 2606 OID 24755)
-- Name: carrera_ciclo uq_carrera_ciclo; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT uq_carrera_ciclo UNIQUE (id_carrera, id_ciclo);


--
-- TOC entry 5185 (class 2606 OID 24739)
-- Name: carrera uq_carrera_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera
    ADD CONSTRAINT uq_carrera_nombre UNIQUE (nombre);


--
-- TOC entry 5181 (class 2606 OID 24722)
-- Name: ciclo_escolar uq_ciclo_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.ciclo_escolar
    ADD CONSTRAINT uq_ciclo_nombre UNIQUE (nombre);


--
-- TOC entry 5252 (class 2606 OID 25104)
-- Name: descuento uq_descuento_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento
    ADD CONSTRAINT uq_descuento_nombre UNIQUE (nombre);


--
-- TOC entry 5198 (class 2606 OID 24806)
-- Name: estudiante uq_estudiante_codigo; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT uq_estudiante_codigo UNIQUE (codigo_estudiante);


--
-- TOC entry 5200 (class 2606 OID 24808)
-- Name: estudiante uq_estudiante_cui; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.estudiante
    ADD CONSTRAINT uq_estudiante_cui UNIQUE (cui);


--
-- TOC entry 5210 (class 2606 OID 24861)
-- Name: expediente uq_expediente_estudiante; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT uq_expediente_estudiante UNIQUE (id_estudiante);


--
-- TOC entry 5193 (class 2606 OID 24780)
-- Name: grado uq_grado_carrera_ciclo_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT uq_grado_carrera_ciclo_nombre UNIQUE (id_carrera_ciclo, nombre);


--
-- TOC entry 5292 (class 2606 OID 25374)
-- Name: permiso uq_permiso_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.permiso
    ADD CONSTRAINT uq_permiso_nombre UNIQUE (nombre);


--
-- TOC entry 5238 (class 2606 OID 25039)
-- Name: recibo uq_recibo_codigo; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_codigo UNIQUE (codigo_verificacion);


--
-- TOC entry 5240 (class 2606 OID 25037)
-- Name: recibo uq_recibo_numero; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_numero UNIQUE (numero_recibo);


--
-- TOC entry 5242 (class 2606 OID 25035)
-- Name: recibo uq_recibo_pago; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT uq_recibo_pago UNIQUE (id_pago);


--
-- TOC entry 5288 (class 2606 OID 25361)
-- Name: rol uq_rol_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol
    ADD CONSTRAINT uq_rol_nombre UNIQUE (nombre);


--
-- TOC entry 5269 (class 2606 OID 25233)
-- Name: solvencia uq_solvencia_codigo; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT uq_solvencia_codigo UNIQUE (codigo_verificacion);


--
-- TOC entry 5214 (class 2606 OID 24883)
-- Name: tipo_documento uq_tipo_documento_nombre; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.tipo_documento
    ADD CONSTRAINT uq_tipo_documento_nombre UNIQUE (nombre);


--
-- TOC entry 5280 (class 2606 OID 25341)
-- Name: usuario uq_usuario_empleado; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT uq_usuario_empleado UNIQUE (id_empleado);


--
-- TOC entry 5282 (class 2606 OID 25339)
-- Name: usuario uq_usuario_username; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT uq_usuario_username UNIQUE (username);


--
-- TOC entry 5284 (class 2606 OID 25337)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 5294 (class 2606 OID 25381)
-- Name: usuario_rol usuario_rol_pkey; Type: CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT usuario_rol_pkey PRIMARY KEY (id_usuario, id_rol);


--
-- TOC entry 5231 (class 1259 OID 25434)
-- Name: idx_aplicacion_obligacion; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_aplicacion_obligacion ON school.aplicacion_pago USING btree (id_obligacion);


--
-- TOC entry 5232 (class 1259 OID 25433)
-- Name: idx_aplicacion_pago; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_aplicacion_pago ON school.aplicacion_pago USING btree (id_pago);


--
-- TOC entry 5299 (class 1259 OID 25443)
-- Name: idx_auditoria_fecha; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_auditoria_fecha ON school.auditoria USING btree (fecha_evento);


--
-- TOC entry 5300 (class 1259 OID 25442)
-- Name: idx_auditoria_usuario; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_auditoria_usuario ON school.auditoria USING btree (id_usuario);


--
-- TOC entry 5272 (class 1259 OID 25441)
-- Name: idx_contacto_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_contacto_estudiante ON school.contacto USING btree (id_estudiante);


--
-- TOC entry 5217 (class 1259 OID 25440)
-- Name: idx_documento_expediente; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_documento_expediente ON school.documento_expediente USING btree (id_expediente);


--
-- TOC entry 5196 (class 1259 OID 25444)
-- Name: idx_estudiante_activo; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_estudiante_activo ON school.estudiante USING btree (id_estudiante) WHERE (estado = 'ACTIVO'::school.estado_estudiante);


--
-- TOC entry 5201 (class 1259 OID 25445)
-- Name: idx_inscripcion_activa; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_activa ON school.inscripcion USING btree (id_estudiante) WHERE (estado = 'ACTIVA'::school.estado_inscripcion);


--
-- TOC entry 5202 (class 1259 OID 25427)
-- Name: idx_inscripcion_carrera_ciclo; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_carrera_ciclo ON school.inscripcion USING btree (id_carrera_ciclo);


--
-- TOC entry 5203 (class 1259 OID 25426)
-- Name: idx_inscripcion_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_estudiante ON school.inscripcion USING btree (id_estudiante);


--
-- TOC entry 5204 (class 1259 OID 25428)
-- Name: idx_inscripcion_grado; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_inscripcion_grado ON school.inscripcion USING btree (id_grado);


--
-- TOC entry 5257 (class 1259 OID 25439)
-- Name: idx_movimiento_destino; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_movimiento_destino ON school.movimiento_saldo USING btree (id_inscripcion_destino);


--
-- TOC entry 5258 (class 1259 OID 25437)
-- Name: idx_movimiento_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_movimiento_estudiante ON school.movimiento_saldo USING btree (id_estudiante);


--
-- TOC entry 5259 (class 1259 OID 25438)
-- Name: idx_movimiento_origen; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_movimiento_origen ON school.movimiento_saldo USING btree (id_inscripcion_origen);


--
-- TOC entry 5220 (class 1259 OID 25430)
-- Name: idx_obligacion_fecha_vencimiento; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_obligacion_fecha_vencimiento ON school.obligacion USING btree (fecha_vencimiento);


--
-- TOC entry 5221 (class 1259 OID 25429)
-- Name: idx_obligacion_inscripcion; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_obligacion_inscripcion ON school.obligacion USING btree (id_inscripcion);


--
-- TOC entry 5222 (class 1259 OID 25446)
-- Name: idx_obligacion_pendiente; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_obligacion_pendiente ON school.obligacion USING btree (id_inscripcion) WHERE (estado = ANY (ARRAY['PENDIENTE'::school.estado_obligacion, 'PARCIAL'::school.estado_obligacion]));


--
-- TOC entry 5225 (class 1259 OID 25431)
-- Name: idx_pago_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_pago_estudiante ON school.pago USING btree (id_estudiante);


--
-- TOC entry 5226 (class 1259 OID 25432)
-- Name: idx_pago_fecha; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_pago_fecha ON school.pago USING btree (fecha_pago);


--
-- TOC entry 5264 (class 1259 OID 25435)
-- Name: idx_solvencia_estudiante; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_solvencia_estudiante ON school.solvencia USING btree (id_estudiante);


--
-- TOC entry 5265 (class 1259 OID 25436)
-- Name: idx_solvencia_evaluacion; Type: INDEX; Schema: school; Owner: postgres
--

CREATE INDEX idx_solvencia_evaluacion ON school.solvencia USING btree (id_evaluacion);


--
-- TOC entry 5487 (class 2618 OID 25450)
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
-- TOC entry 5314 (class 2606 OID 25016)
-- Name: aplicacion_pago fk_aplicacion_obligacion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT fk_aplicacion_obligacion FOREIGN KEY (id_obligacion) REFERENCES school.obligacion(id_obligacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5315 (class 2606 OID 25011)
-- Name: aplicacion_pago fk_aplicacion_pago; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.aplicacion_pago
    ADD CONSTRAINT fk_aplicacion_pago FOREIGN KEY (id_pago) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5339 (class 2606 OID 25421)
-- Name: auditoria fk_auditoria_usuario; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.auditoria
    ADD CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES school.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 5317 (class 2606 OID 25077)
-- Name: beca_estudiante fk_beca_estudiante_beca; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT fk_beca_estudiante_beca FOREIGN KEY (id_beca) REFERENCES school.beca(id_beca) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5318 (class 2606 OID 25082)
-- Name: beca_estudiante fk_beca_estudiante_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.beca_estudiante
    ADD CONSTRAINT fk_beca_estudiante_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5321 (class 2606 OID 25145)
-- Name: cambio_carrera fk_cambio_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5322 (class 2606 OID 25155)
-- Name: cambio_carrera fk_cambio_inscripcion_destino; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_inscripcion_destino FOREIGN KEY (id_inscripcion_destino) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5323 (class 2606 OID 25150)
-- Name: cambio_carrera fk_cambio_inscripcion_origen; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.cambio_carrera
    ADD CONSTRAINT fk_cambio_inscripcion_origen FOREIGN KEY (id_inscripcion_origen) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5301 (class 2606 OID 24756)
-- Name: carrera_ciclo fk_carrera_ciclo_carrera; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT fk_carrera_ciclo_carrera FOREIGN KEY (id_carrera) REFERENCES school.carrera(id_carrera) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5302 (class 2606 OID 24761)
-- Name: carrera_ciclo fk_carrera_ciclo_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.carrera_ciclo
    ADD CONSTRAINT fk_carrera_ciclo_ciclo FOREIGN KEY (id_ciclo) REFERENCES school.ciclo_escolar(id_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5331 (class 2606 OID 25263)
-- Name: contacto fk_contacto_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.contacto
    ADD CONSTRAINT fk_contacto_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5319 (class 2606 OID 25119)
-- Name: descuento_obligacion fk_descuento_obligacion_descuento; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT fk_descuento_obligacion_descuento FOREIGN KEY (id_descuento) REFERENCES school.descuento(id_descuento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5320 (class 2606 OID 25124)
-- Name: descuento_obligacion fk_descuento_obligacion_obligacion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.descuento_obligacion
    ADD CONSTRAINT fk_descuento_obligacion_obligacion FOREIGN KEY (id_obligacion) REFERENCES school.obligacion(id_obligacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5308 (class 2606 OID 24900)
-- Name: documento_expediente fk_documento_expediente; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT fk_documento_expediente FOREIGN KEY (id_expediente) REFERENCES school.expediente(id_expediente) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5309 (class 2606 OID 24905)
-- Name: documento_expediente fk_documento_tipo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.documento_expediente
    ADD CONSTRAINT fk_documento_tipo FOREIGN KEY (id_tipo_documento) REFERENCES school.tipo_documento(id_tipo_documento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5327 (class 2606 OID 25207)
-- Name: evaluacion fk_evaluacion_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.evaluacion
    ADD CONSTRAINT fk_evaluacion_ciclo FOREIGN KEY (id_ciclo) REFERENCES school.ciclo_escolar(id_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5307 (class 2606 OID 24862)
-- Name: expediente fk_expediente_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.expediente
    ADD CONSTRAINT fk_expediente_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5303 (class 2606 OID 24781)
-- Name: grado fk_grado_carrera_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.grado
    ADD CONSTRAINT fk_grado_carrera_ciclo FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5304 (class 2606 OID 24835)
-- Name: inscripcion fk_inscripcion_carrera_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT fk_inscripcion_carrera_ciclo FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5305 (class 2606 OID 24830)
-- Name: inscripcion fk_inscripcion_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT fk_inscripcion_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5306 (class 2606 OID 24840)
-- Name: inscripcion fk_inscripcion_grado; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.inscripcion
    ADD CONSTRAINT fk_inscripcion_grado FOREIGN KEY (id_grado) REFERENCES school.grado(id_grado) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5324 (class 2606 OID 25188)
-- Name: movimiento_saldo fk_movimiento_destino; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_destino FOREIGN KEY (id_inscripcion_destino) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5325 (class 2606 OID 25178)
-- Name: movimiento_saldo fk_movimiento_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5326 (class 2606 OID 25183)
-- Name: movimiento_saldo fk_movimiento_origen; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.movimiento_saldo
    ADD CONSTRAINT fk_movimiento_origen FOREIGN KEY (id_inscripcion_origen) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5332 (class 2606 OID 25302)
-- Name: notificacion_destinatario fk_notificacion_contacto; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT fk_notificacion_contacto FOREIGN KEY (id_contacto) REFERENCES school.contacto(id_contacto) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5333 (class 2606 OID 25297)
-- Name: notificacion_destinatario fk_notificacion_destinatario; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.notificacion_destinatario
    ADD CONSTRAINT fk_notificacion_destinatario FOREIGN KEY (id_notificacion) REFERENCES school.notificacion(id_notificacion) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 5311 (class 2606 OID 24959)
-- Name: obligacion fk_obligacion_inscripcion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT fk_obligacion_inscripcion FOREIGN KEY (id_inscripcion) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5312 (class 2606 OID 24964)
-- Name: obligacion fk_obligacion_precio; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.obligacion
    ADD CONSTRAINT fk_obligacion_precio FOREIGN KEY (id_precio) REFERENCES school.precio_carrera(id_precio) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5313 (class 2606 OID 24989)
-- Name: pago fk_pago_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.pago
    ADD CONSTRAINT fk_pago_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5310 (class 2606 OID 24929)
-- Name: precio_carrera fk_precio_carrera_ciclo; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.precio_carrera
    ADD CONSTRAINT fk_precio_carrera_ciclo FOREIGN KEY (id_carrera_ciclo) REFERENCES school.carrera_ciclo(id_carrera_ciclo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5316 (class 2606 OID 25040)
-- Name: recibo fk_recibo_pago; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.recibo
    ADD CONSTRAINT fk_recibo_pago FOREIGN KEY (id_pago) REFERENCES school.pago(id_pago) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5337 (class 2606 OID 25404)
-- Name: rol_permiso fk_rol_permiso_permiso; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT fk_rol_permiso_permiso FOREIGN KEY (id_permiso) REFERENCES school.permiso(id_permiso) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5338 (class 2606 OID 25399)
-- Name: rol_permiso fk_rol_permiso_rol; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.rol_permiso
    ADD CONSTRAINT fk_rol_permiso_rol FOREIGN KEY (id_rol) REFERENCES school.rol(id_rol) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5328 (class 2606 OID 25234)
-- Name: solvencia fk_solvencia_estudiante; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_estudiante FOREIGN KEY (id_estudiante) REFERENCES school.estudiante(id_estudiante) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5329 (class 2606 OID 25244)
-- Name: solvencia fk_solvencia_evaluacion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_evaluacion FOREIGN KEY (id_evaluacion) REFERENCES school.evaluacion(id_evaluacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5330 (class 2606 OID 25239)
-- Name: solvencia fk_solvencia_inscripcion; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.solvencia
    ADD CONSTRAINT fk_solvencia_inscripcion FOREIGN KEY (id_inscripcion) REFERENCES school.inscripcion(id_inscripcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5334 (class 2606 OID 25342)
-- Name: usuario fk_usuario_empleado; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario
    ADD CONSTRAINT fk_usuario_empleado FOREIGN KEY (id_empleado) REFERENCES school.empleado(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5335 (class 2606 OID 25387)
-- Name: usuario_rol fk_usuario_rol_rol; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_rol FOREIGN KEY (id_rol) REFERENCES school.rol(id_rol) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 5336 (class 2606 OID 25382)
-- Name: usuario_rol fk_usuario_rol_usuario; Type: FK CONSTRAINT; Schema: school; Owner: postgres
--

ALTER TABLE ONLY school.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_usuario FOREIGN KEY (id_usuario) REFERENCES school.usuario(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT;


-- Completed on 2026-09-07 21:56:29

--
-- PostgreSQL database dump complete
--

\unrestrict IqAxzaISGSYKbEmSNcbzWvO14gJcvrnUJAWn4VWbpQyUSQgvUirikRYOhqTiyne

