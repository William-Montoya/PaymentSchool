export type EstadoDestinatario =
  | 'GENERADO'
  | 'ABIERTO'


export interface NotificacionContacto {
  id_contacto: number
  id_estudiante: number

  codigo_estudiante: string
  estudiante: string

  contacto: string
  parentesco: string | null

  telefono: string | null
  whatsapp: string | null
  email: string | null

  es_principal: boolean
}


export interface NotificacionDestinatario {
  id_destinatario: number
  id_contacto: number

  contacto: string

  id_estudiante: number
  codigo_estudiante: string
  estudiante: string

  telefono: string | null
  whatsapp: string | null
  email: string | null

  es_principal: boolean

  estado: EstadoDestinatario

  fecha_generado: string
  fecha_abierto: string | null
}


export interface NotificacionResumen {
  id_notificacion: number

  titulo: string
  mensaje: string

  fecha_creacion: string
  id_usuario: number | null

  total_destinatarios: number
  total_abiertos: number
  total_pendientes: number
}


export interface NotificacionDetalle
  extends NotificacionResumen {
  destinatarios: NotificacionDestinatario[]
}


export interface NotificacionDeuda
  extends NotificacionDetalle {
  deuda_total: string
}


export interface NotificacionCreate {
  titulo: string
  mensaje: string
  ids_contacto: number[]
}


export interface NotificacionDeudaCreate {
  id_contacto?: number | null
}


export interface NotificacionListParams {
  id_estudiante?: number
  estado_destinatario?: EstadoDestinatario
  offset?: number
  limit?: number
}


export interface NotificacionContactoListParams {
  buscar?: string
  limit?: number
}
