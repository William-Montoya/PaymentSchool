export type TipoInscripcion =
  | 'NUEVA'
  | 'REINSCRIPCION'
  | 'TRASLADO'


export type EstadoInscripcion =
  | 'ACTIVA'
  | 'FINALIZADA'
  | 'CANCELADA'
  | 'RETIRADA'


export interface InscripcionCreate {
  id_estudiante: number
  id_carrera_ciclo: number
  id_grado: number
  tipo: TipoInscripcion
  observaciones?: string | null
}


export interface InscripcionDetalle {
  id_inscripcion: number
  id_estudiante: number
  id_carrera_ciclo: number
  id_grado: number

  fecha_inscripcion: string
  tipo: TipoInscripcion
  estado: EstadoInscripcion

  observaciones: string | null
  creado_en: string

  codigo_estudiante: string
  estudiante: string

  carrera: string
  ciclo: string
  grado: string
}


export interface InscripcionListParams {
  id_estudiante?: number
  id_ciclo?: number
  id_carrera?: number
  estado?: EstadoInscripcion
}