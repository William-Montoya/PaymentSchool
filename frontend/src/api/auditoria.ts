import apiClient from './client'

import type {
  AuditoriaCatalogos,
  AuditoriaListParams,
  AuditoriaRegistro,
} from '../types/auditoria'


export async function getAuditorias(
  params: AuditoriaListParams = {},
): Promise<AuditoriaRegistro[]> {
  const response =
    await apiClient.get<AuditoriaRegistro[]>(
      '/auditoria',
      {
        params,
      },
    )

  return response.data
}


export async function getAuditoria(
  idAuditoria: number,
): Promise<AuditoriaRegistro> {
  const response =
    await apiClient.get<AuditoriaRegistro>(
      `/auditoria/${idAuditoria}`,
    )

  return response.data
}


export async function getAuditoriaCatalogos():
Promise<AuditoriaCatalogos> {
  const response =
    await apiClient.get<AuditoriaCatalogos>(
      '/auditoria/catalogos',
    )

  return response.data
}
