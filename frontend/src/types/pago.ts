export type MetodoPago =
  | 'EFECTIVO'
  | 'TRANSFERENCIA'
  | 'DEPOSITO'
  | 'TARJETA'
  | 'OTRO'

export type EstadoPago =
  | 'PENDIENTE'
  | 'CONFIRMADO'
  | 'ANULADO'

export type TipoObligacionPago =
  | 'INSCRIPCION'
  | 'MENSUALIDAD'
  | 'CERTIFICACION'
  | 'CONSTANCIA'
  | 'OTRO'

export interface PagoResponse {
  id_pago: number
  id_estudiante: number
  id_usuario: number | null

  fecha_pago: string
  monto_total: string

  metodo: MetodoPago
  referencia: string | null
  observaciones: string | null

  estado: EstadoPago
  creado_en: string

  total_aplicado: string
  saldo_disponible: string | null
}

export interface AplicacionPagoDetalle {
  id_aplicacion: number
  id_pago: number
  id_obligacion: number

  concepto: string
  periodo: string | null
  tipo_obligacion: TipoObligacionPago
  fecha_vencimiento: string | null

  monto_obligacion: string
  monto_aplicado: string
  fecha_aplicacion: string
}

export interface ReciboPago {
  id_recibo: number
  id_pago: number
  numero_recibo: string
  codigo_verificacion: string
  fecha_emision: string
}

export interface CobroCreate {
  id_estudiante: number
  id_obligaciones: number[]
  monto: string
  metodo: MetodoPago
  referencia?: string | null
  observaciones?: string | null
}

export interface CobroResponse {
  pago: PagoResponse
  recibo: ReciboPago
  aplicaciones: AplicacionPagoDetalle[]
  total_seleccionado: string
  total_aplicado: string
  saldo_seleccionado_restante: string
}

export interface ComprobantePagoResponse {
  pago: PagoResponse
  recibo: ReciboPago | null
  aplicaciones: AplicacionPagoDetalle[]
}

export interface PagoListParams {
  id_estudiante?: number
  estado?: EstadoPago
}
