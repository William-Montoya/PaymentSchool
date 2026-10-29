import apiClient from './client'

import type {
  EstadoEstudiante,
  Estudiante,
  EstudianteCreate,
  EstudianteListParams,
  EstudianteUpdate,
} from '../types/estudiante'

export async function getEstudiantes(
  params: EstudianteListParams,
): Promise<Estudiante[]> {
  const response =
    await apiClient.get<Estudiante[]>(
      '/estudiantes',
      {
        params,
      },
    )

  return response.data
}

export async function getEstudiante(
  idEstudiante: number,
): Promise<Estudiante> {
  const response =
    await apiClient.get<Estudiante>(
      `/estudiantes/${idEstudiante}`,
    )

  return response.data
}

export async function createEstudiante(
  payload: EstudianteCreate,
): Promise<Estudiante> {
  const response =
    await apiClient.post<Estudiante>(
      '/estudiantes',
      payload,
    )

  return response.data
}

export async function updateEstudiante(
  idEstudiante: number,
  payload: EstudianteUpdate,
): Promise<Estudiante> {
  const response =
    await apiClient.put<Estudiante>(
      `/estudiantes/${idEstudiante}`,
      payload,
    )

  return response.data
}

export async function updateEstadoEstudiante(
  idEstudiante: number,
  estado: EstadoEstudiante,
): Promise<Estudiante> {
  const response =
    await apiClient.patch<Estudiante>(
      `/estudiantes/${idEstudiante}/estado`,
      {
        estado,
      },
    )

  return response.data
}