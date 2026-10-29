import apiClient from './client'

import type {
  DocumentoExpediente,
  ExpedienteCreate,
  ExpedienteDetalle,
  ExpedienteUpdate,
} from '../types/expediente'


export async function getExpedienteByEstudiante(
  idEstudiante: number,
): Promise<ExpedienteDetalle> {
  const response =
    await apiClient.get<ExpedienteDetalle>(
      `/expedientes/estudiante/${idEstudiante}`,
    )

  return response.data
}


export async function createExpediente(
  payload: ExpedienteCreate,
): Promise<ExpedienteDetalle> {
  const response =
    await apiClient.post<ExpedienteDetalle>(
      '/expedientes',
      payload,
    )

  return response.data
}


export async function updateExpediente(
  idExpediente: number,
  payload: ExpedienteUpdate,
): Promise<ExpedienteDetalle> {
  const response =
    await apiClient.patch<ExpedienteDetalle>(
      `/expedientes/${idExpediente}`,
      payload,
    )

  return response.data
}


export async function updateDocumentoEntrega(
  idExpediente: number,
  idTipoDocumento: number,
  entregado: boolean,
): Promise<DocumentoExpediente> {
  const response =
    await apiClient.patch<
      DocumentoExpediente
    >(
      (
        `/expedientes/${idExpediente}` +
        `/documentos/${idTipoDocumento}` +
        '/entrega'
      ),
      {
        entregado,
      },
    )

  return response.data
}


export async function uploadDocumento(
  idExpediente: number,
  idTipoDocumento: number,
  archivo: File,
): Promise<DocumentoExpediente> {
  const formData =
    new FormData()

  formData.append(
    'archivo',
    archivo,
  )

  const response =
    await apiClient.post<
      DocumentoExpediente
    >(
      (
        `/expedientes/${idExpediente}` +
        `/documentos/${idTipoDocumento}`
      ),
      formData,
    )

  return response.data
}


export async function replaceDocumentoArchivo(
  idExpediente: number,
  idDocumento: number,
  archivo: File,
): Promise<DocumentoExpediente> {
  const formData =
    new FormData()

  formData.append(
    'archivo',
    archivo,
  )

  const response =
    await apiClient.put<
      DocumentoExpediente
    >(
      (
        `/expedientes/${idExpediente}` +
        `/documentos/${idDocumento}` +
        '/archivo'
      ),
      formData,
    )

  return response.data
}


export async function getDocumentoArchivo(
  idExpediente: number,
  idDocumento: number,
): Promise<Blob> {
  const response =
    await apiClient.get<Blob>(
      (
        `/expedientes/${idExpediente}` +
        `/documentos/${idDocumento}` +
        '/descargar'
      ),
      {
        responseType: 'blob',
      },
    )

  return response.data
}