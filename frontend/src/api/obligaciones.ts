import apiClient from './client'

import type {
  GenerarMensualidadesCreate,
  GenerarMensualidadesResponse,
  InscripcionFinanzas,
  InscripcionFinanzasListParams,
  ObligacionDesdePrecioCreate,
  ObligacionListParams,
  ObligacionManualCreate,
  ObligacionSaldo,
} from '../types/obligacion'


export async function getInscripcionesFinanzas(
  params:
    InscripcionFinanzasListParams = {},
): Promise<InscripcionFinanzas[]> {
  const response =
    await apiClient.get<
      InscripcionFinanzas[]
    >(
      '/obligaciones/inscripciones',
      {
        params,
      },
    )

  return response.data
}


export async function getObligaciones(
  params: ObligacionListParams = {},
): Promise<ObligacionSaldo[]> {
  const response =
    await apiClient.get<
      ObligacionSaldo[]
    >(
      '/obligaciones',
      {
        params,
      },
    )

  return response.data
}


export async function getObligacion(
  idObligacion: number,
): Promise<ObligacionSaldo> {
  const response =
    await apiClient.get<
      ObligacionSaldo
    >(
      `/obligaciones/${idObligacion}`,
    )

  return response.data
}


export async function createObligacionDesdePrecio(
  payload:
    ObligacionDesdePrecioCreate,
): Promise<ObligacionSaldo> {
  const response =
    await apiClient.post<
      ObligacionSaldo
    >(
      '/obligaciones/desde-precio',
      payload,
    )

  return response.data
}


export async function createObligacionManual(
  payload:
    ObligacionManualCreate,
): Promise<ObligacionSaldo> {
  const response =
    await apiClient.post<
      ObligacionSaldo
    >(
      '/obligaciones/manual',
      payload,
    )

  return response.data
}


export async function generarMensualidades(
  payload:
    GenerarMensualidadesCreate,
): Promise<GenerarMensualidadesResponse> {
  const response =
    await apiClient.post<
      GenerarMensualidadesResponse
    >(
      '/obligaciones/mensualidades',
      payload,
    )

  return response.data
}