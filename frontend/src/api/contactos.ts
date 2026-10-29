import apiClient from './client'

import type {
  Contacto,
  ContactoCreate,
  ContactoUpdate,
} from '../types/contacto'


export async function getContactos(
  idEstudiante: number,
  activo?: boolean,
): Promise<Contacto[]> {
  const response =
    await apiClient.get<Contacto[]>(
      `/contactos/estudiante/${idEstudiante}`,
      {
        params: {
          activo,
        },
      },
    )

  return response.data
}


export async function createContacto(
  payload: ContactoCreate,
): Promise<Contacto> {
  const response =
    await apiClient.post<Contacto>(
      '/contactos',
      payload,
    )

  return response.data
}


export async function updateContacto(
  idContacto: number,
  payload: ContactoUpdate,
): Promise<Contacto> {
  const response =
    await apiClient.put<Contacto>(
      `/contactos/${idContacto}`,
      payload,
    )

  return response.data
}