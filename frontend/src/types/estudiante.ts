export type EstadoEstudiante =
  | 'ACTIVO'
  | 'INACTIVO'
  | 'RETIRADO'
  | 'EGRESADO'


export interface Estudiante {
  id_estudiante: number
  codigo_estudiante: string

  cui: string | null

  nombres: string
  apellidos: string

  fecha_nacimiento:
    string | null

  telefono: string | null
  whatsapp: string | null
  email: string | null

  direccion: string | null

  estado: EstadoEstudiante

  creado_en: string
  actualizado_en: string
}


export interface EstudianteCreate {
  cui: string | null

  nombres: string
  apellidos: string

  fecha_nacimiento:
    string | null

  telefono: string | null
  whatsapp: string | null
  email: string | null

  direccion: string | null
}


export interface EstudianteUpdate {
  cui?: string | null

  nombres?: string | null
  apellidos?: string | null

  fecha_nacimiento?:
    string | null

  telefono?: string | null
  whatsapp?: string | null
  email?: string | null

  direccion?: string | null
}


export interface EstudianteListParams {
  offset?: number
  limit?: number

  estado?: EstadoEstudiante
  buscar?: string
}