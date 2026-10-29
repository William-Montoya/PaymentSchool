import apiClient from './client'

import type {
  Empleado,
  EmpleadoCreate,
  EmpleadoUpdate,
  EstadoUsuario,
  Permiso,
  PermisoCreate,
  PermisoUpdate,
  RolCreate,
  RolDetalle,
  RolUpdate,
  UsuarioCreate,
  UsuarioDetalle,
} from '../types/seguridad'


export async function getEmpleados(
  activo?: boolean,
): Promise<Empleado[]> {
  const response = await apiClient.get<Empleado[]>(
    '/empleados',
    {
      params: {
        activo,
      },
    },
  )

  return response.data
}


export async function createEmpleado(
  payload: EmpleadoCreate,
): Promise<Empleado> {
  const response = await apiClient.post<Empleado>(
    '/empleados',
    payload,
  )

  return response.data
}


export async function updateEmpleado(
  idEmpleado: number,
  payload: EmpleadoUpdate,
): Promise<Empleado> {
  const response = await apiClient.put<Empleado>(
    `/empleados/${idEmpleado}`,
    payload,
  )

  return response.data
}


export async function updateEmpleadoEstado(
  idEmpleado: number,
  activo: boolean,
): Promise<Empleado> {
  const response = await apiClient.patch<Empleado>(
    `/empleados/${idEmpleado}/estado`,
    {
      activo,
    },
  )

  return response.data
}


export async function getPermisos(): Promise<Permiso[]> {
  const response = await apiClient.get<Permiso[]>(
    '/permisos',
  )

  return response.data
}


export async function createPermiso(
  payload: PermisoCreate,
): Promise<Permiso> {
  const response = await apiClient.post<Permiso>(
    '/permisos',
    payload,
  )

  return response.data
}


export async function updatePermiso(
  idPermiso: number,
  payload: PermisoUpdate,
): Promise<Permiso> {
  const response = await apiClient.patch<Permiso>(
    `/permisos/${idPermiso}`,
    payload,
  )

  return response.data
}


export async function getRoles(
  activo?: boolean,
): Promise<RolDetalle[]> {
  const response = await apiClient.get<RolDetalle[]>(
    '/roles',
    {
      params: {
        activo,
      },
    },
  )

  return response.data
}


export async function createRol(
  payload: RolCreate,
): Promise<RolDetalle> {
  const response = await apiClient.post<RolDetalle>(
    '/roles',
    payload,
  )

  return response.data
}


export async function updateRol(
  idRol: number,
  payload: RolUpdate,
): Promise<RolDetalle> {
  const response = await apiClient.patch<RolDetalle>(
    `/roles/${idRol}`,
    payload,
  )

  return response.data
}


export async function updateRolEstado(
  idRol: number,
  activo: boolean,
): Promise<RolDetalle> {
  const response = await apiClient.patch<RolDetalle>(
    `/roles/${idRol}/estado`,
    {
      activo,
    },
  )

  return response.data
}


export async function updateRolPermisos(
  idRol: number,
  idsPermiso: number[],
): Promise<RolDetalle> {
  const response = await apiClient.put<RolDetalle>(
    `/roles/${idRol}/permisos`,
    {
      ids_permiso: idsPermiso,
    },
  )

  return response.data
}


export async function getUsuarios(
  estado?: EstadoUsuario,
): Promise<UsuarioDetalle[]> {
  const response = await apiClient.get<UsuarioDetalle[]>(
    '/usuarios',
    {
      params: {
        estado,
      },
    },
  )

  return response.data
}


export async function createUsuario(
  payload: UsuarioCreate,
): Promise<UsuarioDetalle> {
  const response = await apiClient.post<UsuarioDetalle>(
    '/usuarios',
    payload,
  )

  return response.data
}


export async function updateUsuarioRoles(
  idUsuario: number,
  idsRol: number[],
): Promise<UsuarioDetalle> {
  const response = await apiClient.put<UsuarioDetalle>(
    `/usuarios/${idUsuario}/roles`,
    {
      ids_rol: idsRol,
    },
  )

  return response.data
}


export async function updateUsuarioEstado(
  idUsuario: number,
  estado: EstadoUsuario,
): Promise<UsuarioDetalle> {
  const response = await apiClient.patch<UsuarioDetalle>(
    `/usuarios/${idUsuario}/estado`,
    {
      estado,
    },
  )

  return response.data
}


export async function updateUsuarioPassword(
  idUsuario: number,
  nuevaPassword: string,
): Promise<UsuarioDetalle> {
  const response = await apiClient.patch<UsuarioDetalle>(
    `/usuarios/${idUsuario}/password`,
    {
      nueva_password: nuevaPassword,
    },
  )

  return response.data
}
