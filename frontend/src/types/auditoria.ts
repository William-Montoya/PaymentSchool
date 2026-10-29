export interface AuditoriaRegistro {
  id_auditoria: number

  id_usuario: number | null
  username: string | null

  fecha_evento: string

  modulo: string | null
  accion: string | null

  tabla_afectada: string | null
  id_registro: number | null

  descripcion: string | null

  datos_anteriores: Record<string, unknown> | null
  datos_nuevos: Record<string, unknown> | null

  ip: string | null
}


export interface AuditoriaUsuarioFiltro {
  id_usuario: number
  username: string
}


export interface AuditoriaCatalogos {
  usuarios: AuditoriaUsuarioFiltro[]
  modulos: string[]
  acciones: string[]
  tablas: string[]
}


export interface AuditoriaListParams {
  id_usuario?: number
  modulo?: string
  accion?: string
  tabla_afectada?: string
  id_registro?: number
  fecha_desde?: string
  fecha_hasta?: string
  offset?: number
  limit?: number
}
