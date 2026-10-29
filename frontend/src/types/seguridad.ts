export interface Empleado {
  id_empleado: number
  nombres: string
  apellidos: string
  telefono: string | null
  email: string | null
  cargo: string | null
  activo: boolean
  creado_en: string
}

export interface EmpleadoCreate {
  nombres: string
  apellidos: string
  telefono?: string | null
  email?: string | null
  cargo?: string | null
}

export interface EmpleadoUpdate {
  nombres?: string
  apellidos?: string
  telefono?: string | null
  email?: string | null
  cargo?: string | null
}

export interface Permiso {
  id_permiso: number
  nombre: string
  descripcion: string | null
}

export interface PermisoCreate {
  nombre: string
  descripcion?: string | null
}

export interface PermisoUpdate {
  descripcion?: string | null
}

export interface Rol {
  id_rol: number
  nombre: string
  descripcion: string | null
  activo: boolean
}

export interface RolDetalle extends Rol {
  permisos: Permiso[]
}

export interface RolCreate {
  nombre: string
  descripcion?: string | null
}

export interface RolUpdate {
  descripcion?: string | null
}

export interface UsuarioRol {
  id_rol: number
  nombre: string
  descripcion: string | null
  activo: boolean
}

export type EstadoUsuario =
  | 'ACTIVO'
  | 'INACTIVO'
  | 'BLOQUEADO'

export interface UsuarioDetalle {
  id_usuario: number
  id_empleado: number | null
  empleado: string | null
  cargo: string | null
  username: string
  estado: EstadoUsuario
  ultimo_acceso: string | null
  creado_en: string
  roles: UsuarioRol[]
  permisos: Permiso[]
}

export interface UsuarioCreate {
  id_empleado: number
  username: string
  password: string
  ids_rol: number[]
}
