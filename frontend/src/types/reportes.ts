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

export interface EstudianteInsolvente {
  id_estudiante: number
  codigo_estudiante: string
  estudiante: string
  id_inscripcion: number
  grado: string
  deuda_total: string
}

export interface DashboardOverview {
  resumen: DashboardFinanciero
  deudaPorGrado: DeudaPorGrado[]
  estudiantesInsolventes:
    EstudianteInsolvente[]
}