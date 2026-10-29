import apiClient from './client'

import type {
  Carrera,
  CarreraCiclo,
  CarreraCicloCreate,
  CarreraCicloListParams,
  CarreraCreate,
  CicloCreate,
  CicloEscolar,
  Grado,
  GradoCreate,
  GradoListParams,
} from '../types/catalogoAcademico'


export async function getCiclos():
Promise<CicloEscolar[]> {
  const response =
    await apiClient.get<CicloEscolar[]>(
      '/ciclos',
    )

  return response.data
}


export async function createCiclo(
  payload: CicloCreate,
): Promise<CicloEscolar> {
  const response =
    await apiClient.post<CicloEscolar>(
      '/ciclos',
      payload,
    )

  return response.data
}


export async function getCarreras():
Promise<Carrera[]> {
  const response =
    await apiClient.get<Carrera[]>(
      '/carreras',
    )

  return response.data
}


export async function createCarrera(
  payload: CarreraCreate,
): Promise<Carrera> {
  const response =
    await apiClient.post<Carrera>(
      '/carreras',
      payload,
    )

  return response.data
}


export async function getCarreraCiclos(
  params: CarreraCicloListParams,
): Promise<CarreraCiclo[]> {
  const response =
    await apiClient.get<CarreraCiclo[]>(
      '/carrera-ciclos',
      {
        params,
      },
    )

  return response.data
}


export async function createCarreraCiclo(
  payload: CarreraCicloCreate,
): Promise<CarreraCiclo> {
  const response =
    await apiClient.post<CarreraCiclo>(
      '/carrera-ciclos',
      payload,
    )

  return response.data
}


export async function getGrados(
  params: GradoListParams,
): Promise<Grado[]> {
  const response =
    await apiClient.get<Grado[]>(
      '/grados',
      {
        params,
      },
    )

  return response.data
}


export async function createGrado(
  payload: GradoCreate,
): Promise<Grado> {
  const response =
    await apiClient.post<Grado>(
      '/grados',
      payload,
    )

  return response.data
}