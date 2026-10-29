import apiClient from './client'

import type {
  NotificacionContacto,
  NotificacionContactoListParams,
  NotificacionCreate,
  NotificacionDeuda,
  NotificacionDeudaCreate,
  NotificacionDestinatario,
  NotificacionDetalle,
  NotificacionListParams,
  NotificacionResumen,
} from '../types/notificacion'


export async function getNotificaciones(
  params: NotificacionListParams = {},
): Promise<NotificacionResumen[]> {
  const response =
    await apiClient.get<
      NotificacionResumen[]
    >(
      '/notificaciones',
      {
        params,
      },
    )

  return response.data
}


export async function getNotificacion(
  idNotificacion: number,
): Promise<NotificacionDetalle> {
  const response =
    await apiClient.get<
      NotificacionDetalle
    >(
      `/notificaciones/${idNotificacion}`,
    )

  return response.data
}


export async function buscarContactosNotificacion(
  params:
    NotificacionContactoListParams = {},
): Promise<NotificacionContacto[]> {
  const response =
    await apiClient.get<
      NotificacionContacto[]
    >(
      '/notificaciones/contactos',
      {
        params,
      },
    )

  return response.data
}


export async function createNotificacion(
  payload: NotificacionCreate,
): Promise<NotificacionDetalle> {
  const response =
    await apiClient.post<
      NotificacionDetalle
    >(
      '/notificaciones',
      payload,
    )

  return response.data
}


export async function createAvisoDeuda(
  idEstudiante: number,
  payload: NotificacionDeudaCreate,
): Promise<NotificacionDeuda> {
  const response =
    await apiClient.post<
      NotificacionDeuda
    >(
      `/notificaciones/deuda/${idEstudiante}`,
      payload,
    )

  return response.data
}


export async function marcarDestinatarioAbierto(
  idDestinatario: number,
): Promise<NotificacionDestinatario> {
  const response =
    await apiClient.patch<
      NotificacionDestinatario
    >(
      (
        '/notificaciones/destinatarios/' +
        `${idDestinatario}/abrir`
      ),
    )

  return response.data
}
