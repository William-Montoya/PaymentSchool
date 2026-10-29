export type UsuarioEstado =
  | 'ACTIVO'
  | 'INACTIVO'
  | 'BLOQUEADO'

export interface Permiso {
  id_permiso: number
  nombre: string
  descripcion: string | null
}

export interface UsuarioRol {
  id_rol: number
  nombre: string
  descripcion: string | null
  activo: boolean
}

export interface AuthUser {
  id_usuario: number
  id_empleado: number | null
  empleado: string | null
  cargo: string | null
  username: string
  estado: UsuarioEstado
  ultimo_acceso: string | null
  creado_en: string
  roles: UsuarioRol[]
  permisos: Permiso[]
}

export interface TokenResponse {
  access_token: string
  token_type?: 'bearer'
  expires_in: number
}

export interface LoginCredentials {
  username: string
  password: string
}