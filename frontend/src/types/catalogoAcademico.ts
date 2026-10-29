export type EstadoCiclo =
  | 'PLANIFICADO'
  | 'ACTIVO'
  | 'CERRADO'


export interface CicloEscolar {
  id_ciclo: number
  nombre: string
  fecha_inicio: string
  fecha_fin: string
  estado: EstadoCiclo
  creado_en: string
}


export interface CicloCreate {
  nombre: string
  fecha_inicio: string
  fecha_fin: string
  estado?: EstadoCiclo
}


export interface Carrera {
  id_carrera: number
  nombre: string
  descripcion: string | null
  activo: boolean
  creado_en: string
}


export interface CarreraCreate {
  nombre: string
  descripcion?: string | null
}


export interface CarreraCiclo {
  id_carrera_ciclo: number
  id_carrera: number
  id_ciclo: number
  nombre_comercial: string | null
  estado: boolean
  creado_en: string
}


export interface CarreraCicloCreate {
  id_carrera: number
  id_ciclo: number
  nombre_comercial?: string | null
}


export interface CarreraCicloListParams {
  id_ciclo?: number
  id_carrera?: number
}


export interface Grado {
  id_grado: number
  id_carrera_ciclo: number
  nombre: string
  nivel_orden: number | null
  activo: boolean
}


export interface GradoCreate {
  id_carrera_ciclo: number
  nombre: string
  nivel_orden?: number | null
}


export interface GradoListParams {
  id_carrera_ciclo?: number
}