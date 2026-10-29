export type TipoPrecio =
  | 'INSCRIPCION'
  | 'MENSUALIDAD'
  | 'OTRO'


export interface PrecioCarrera {
  id_precio: number
  id_carrera_ciclo: number
  id_grado: number | null
  tipo: TipoPrecio
  concepto: string
  monto: string
  fecha_inicio: string
  fecha_fin: string | null
  activo: boolean
  creado_en: string
}


export interface PrecioCarreraCreate {
  id_carrera_ciclo: number
  id_grado: number
  tipo: TipoPrecio
  concepto: string
  monto: string
  fecha_inicio: string
  fecha_fin?: string | null
}


export interface PrecioCarreraEstadoUpdate {
  activo: boolean
}


export interface PrecioCarreraListParams {
  id_carrera_ciclo?: number
  id_grado?: number
  tipo?: TipoPrecio
  activo?: boolean
}