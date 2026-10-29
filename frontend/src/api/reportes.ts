import apiClient from './client'

import type {
  DashboardFinanciero,
  DashboardOverview,
  DeudaPorEstudiante,
  DeudaPorGrado,
  EstadoCuentaItem,
  EstudianteInsolvente,
  ReporteListParams,
} from '../types/reporte'


export async function getDashboardFinanciero():
Promise<DashboardFinanciero> {
  const response =
    await apiClient.get<DashboardFinanciero>(
      '/reportes/dashboard',
    )

  return response.data
}


export async function getDeudaPorGrado():
Promise<DeudaPorGrado[]> {
  const response =
    await apiClient.get<DeudaPorGrado[]>(
      '/reportes/deuda-por-grado',
    )

  return response.data
}


export async function getDeudaPorEstudiante(
  params: ReporteListParams = {},
): Promise<DeudaPorEstudiante[]> {
  const response =
    await apiClient.get<DeudaPorEstudiante[]>(
      '/reportes/deuda-por-estudiante',
      { params },
    )

  return response.data
}


export async function getEstudiantesInsolventes(
  params: ReporteListParams = {},
): Promise<EstudianteInsolvente[]> {
  const response =
    await apiClient.get<EstudianteInsolvente[]>(
      '/reportes/estudiantes-insolventes',
      { params },
    )

  return response.data
}


export async function getEstadoCuenta(
  idEstudiante: number,
  idInscripcion?: number,
): Promise<EstadoCuentaItem[]> {
  const response =
    await apiClient.get<EstadoCuentaItem[]>(
      `/reportes/estado-cuenta/${idEstudiante}`,
      {
        params: {
          id_inscripcion: idInscripcion,
        },
      },
    )

  return response.data
}


export async function getDashboardOverview():
Promise<DashboardOverview> {
  const [
    resumen,
    deudaPorGrado,
    estudiantesInsolventes,
  ] = await Promise.all([
    getDashboardFinanciero(),
    getDeudaPorGrado(),
    getEstudiantesInsolventes({
      offset: 0,
      limit: 8,
    }),
  ])

  return {
    resumen,
    deudaPorGrado,
    estudiantesInsolventes,
  }
}
