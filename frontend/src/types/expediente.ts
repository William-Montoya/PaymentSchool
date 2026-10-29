export interface EstadoDocumentoExpediente {
  id_tipo_documento: number
  nombre: string
  obligatorio: boolean

  entregado: boolean

  id_documento: number | null
  nombre_archivo: string | null
}


export interface ExpedienteDetalle {
  id_expediente: number
  id_estudiante: number

  observaciones: string | null

  creado_en: string
  actualizado_en: string

  codigo_estudiante: string
  estudiante: string

  documentos_requeridos: number
  documentos_entregados: number
  documentos_pendientes: number

  completo: boolean

  documentos:
    EstadoDocumentoExpediente[]
}


export interface ExpedienteCreate {
  id_estudiante: number
  observaciones?: string | null
}


export interface ExpedienteUpdate {
  observaciones: string | null
}


export interface DocumentoExpediente {
  id_documento: number
  id_expediente: number
  id_tipo_documento: number

  nombre_archivo: string | null

  entregado: boolean
  fecha_entrega: string | null
}


export interface ExpedienteSummary {
  requeridos: number
  entregados: number
  pendientes: number
  completo: boolean
}