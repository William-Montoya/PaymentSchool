import apiClient from './client'

import type {
  PrecioCarrera,
  PrecioCarreraCreate,
  PrecioCarreraEstadoUpdate,
  PrecioCarreraListParams,
} from '../types/precio'


export async function getPrecios(
  params: PrecioCarreraListParams,
): Promise<PrecioCarrera[]> {
  const response =
    await apiClient.get<PrecioCarrera[]>(
      '/precios',
      {
        params,
      },
    )

  return response.data
}


export async function createPrecio(
  payload: PrecioCarreraCreate,
): Promise<PrecioCarrera> {
  const response =
    await apiClient.post<PrecioCarrera>(
      '/precios',
      payload,
    )

  return response.data
}


export async function updatePrecioEstado(
  idPrecio: number,
  payload: PrecioCarreraEstadoUpdate,
): Promise<PrecioCarrera> {
  const response =
    await apiClient.patch<PrecioCarrera>(
      `/precios/${idPrecio}/estado`,
      payload,
    )

  return response.data
}