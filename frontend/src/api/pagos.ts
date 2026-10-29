import apiClient from './client'

import type {
  CobroCreate,
  CobroResponse,
  ComprobantePagoResponse,
  PagoListParams,
  PagoResponse,
  ReciboPago,
} from '../types/pago'

export async function registrarCobro(
  payload: CobroCreate,
): Promise<CobroResponse> {
  const response = await apiClient.post<CobroResponse>(
    '/pagos/cobro',
    payload,
  )

  return response.data
}

export async function getPagos(
  params: PagoListParams = {},
): Promise<PagoResponse[]> {
  const response = await apiClient.get<PagoResponse[]>(
    '/pagos',
    { params },
  )

  return response.data
}

export async function getComprobantePago(
  idPago: number,
): Promise<ComprobantePagoResponse> {
  const response =
    await apiClient.get<ComprobantePagoResponse>(
      `/pagos/${idPago}/comprobante`,
    )

  return response.data
}

export async function generarReciboPago(
  idPago: number,
): Promise<ReciboPago> {
  const response = await apiClient.post<ReciboPago>(
    `/pagos/${idPago}/recibo`,
  )

  return response.data
}
