export interface DashboardFinanciero {
  estudiantes_activos: number
  inscripciones_activas: number
  total_pagado: string
  deuda_total: string
  estudiantes_insolventes: number
}

export interface DeudaPorGrado {
  id_grado: number
  grado: string
  cantidad_estudiantes: number
  deuda_total: string
}

export interface DeudaPorEstudiante {
  id_estudiante: number
  codigo_estudiante: string
  estudiante: string
  grado: string
  deuda_total: string
}

export interface EstudianteInsolvente {
  id_estudiante: number
  codigo_estudiante: string
  estudiante: string
  id_inscripcion: number
  grado: string
  deuda_total: string
}

export interface EstadoCuentaItem {
  id_estudiante: number
  codigo_estudiante: string
  estudiante: string
  id_inscripcion: number
  carrera: string
  grado: string
  id_obligacion: number
  concepto: string
  periodo: string | null
  fecha_vencimiento: string | null
  total_pagado: string
  saldo: string
}

export interface ReporteListParams {
  buscar?: string
  offset?: number
  limit?: number
}

export interface DashboardOverview {
  resumen: DashboardFinanciero
  deudaPorGrado: DeudaPorGrado[]
  estudiantesInsolventes: EstudianteInsolvente[]
}
