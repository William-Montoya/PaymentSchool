import apiClient from './client'

import type {
  InscripcionCreate,
  InscripcionDetalle,
  InscripcionListParams,
} from '../types/inscripcion'


export async function getInscripciones(
  params: InscripcionListParams = {},
): Promise<InscripcionDetalle[]> {
  const response =
    await apiClient.get<
      InscripcionDetalle[]
    >(
      '/inscripciones',
      {
        params,
      },
    )

  return response.data
}


export async function createInscripcion(
  payload: InscripcionCreate,
): Promise<InscripcionDetalle> {
  const response =
    await apiClient.post<
      InscripcionDetalle
    >(
      '/inscripciones',
      payload,
    )

  return response.data
}