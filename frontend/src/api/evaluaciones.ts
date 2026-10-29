import apiClient from './client'

import type {
  EvaluacionDetalle,
} from '../types/evaluacion'

export async function getEvaluacionesActivas():
  Promise<EvaluacionDetalle[]> {
  const response =
    await apiClient.get<
      EvaluacionDetalle[]
    >(
      '/evaluaciones',
      {
        params: {
          activo: true,
        },
      },
    )

  return response.data
}