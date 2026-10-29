import type {
  EstadoInscripcion,
  InscripcionDetalle,
} from './inscripcion'


export type TipoObligacion =
  | 'INSCRIPCION'
  | 'MENSUALIDAD'
  | 'CERTIFICACION'
  | 'CONSTANCIA'
  | 'OTRO'


export type TipoObligacionManual =
  | 'INSCRIPCION'
  | 'CERTIFICACION'
  | 'CONSTANCIA'
  | 'OTRO'


export type EstadoObligacion =
  | 'PENDIENTE'
  | 'PARCIAL'
  | 'PAGADA'
  | 'ANULADA'


export interface ObligacionSaldo {
  id_obligacion: number
  id_inscripcion: number
  id_precio: number | null

  concepto: string
  periodo: string | null

  fecha_vencimiento:
    string | null

  monto_bruto: string
  monto_descuento: string
  monto_beca: string
  monto_neto: string

  estado: EstadoObligacion
  tipo_obligacion:
    TipoObligacion

  creado_en: string

  total_pagado: string
  saldo: string
}


export interface ObligacionDesdePrecioCreate {
  id_inscripcion: number
  id_precio: number
  fecha_vencimiento: string
}


export interface ObligacionManualCreate {
  id_inscripcion: number

  concepto: string

  tipo_obligacion:
    TipoObligacionManual

  periodo?: string | null

  fecha_vencimiento?:
    string | null

  monto_bruto: string
}


export interface GenerarMensualidadesCreate {
  id_inscripcion: number
  id_precio: number

  fecha_inicio: string

  cantidad_meses: number
}


export interface GenerarMensualidadesResponse {
  mensaje: string

  id_inscripcion: number
  id_precio: number

  fecha_inicio: string

  cantidad_meses: number
}


export interface ObligacionListParams {
  id_inscripcion?: number
  estado?: EstadoObligacion

  tipo_obligacion?:
    TipoObligacion
}


export interface InscripcionFinanzasListParams {
  buscar?: string

  estado?: EstadoInscripcion

  limit?: number
}


export type ObligacionCreateMode =
  | 'DESDE_PRECIO'
  | 'MENSUALIDADES'
  | 'MANUAL'


export type ObligacionCreateAction =
  | {
      mode: 'DESDE_PRECIO'
      payload:
        ObligacionDesdePrecioCreate
    }
  | {
      mode: 'MENSUALIDADES'
      payload:
        GenerarMensualidadesCreate
    }
  | {
      mode: 'MANUAL'
      payload:
        ObligacionManualCreate
    }


export type InscripcionFinanzas =
  InscripcionDetalle