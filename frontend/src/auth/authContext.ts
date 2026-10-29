import {
  createContext,
} from 'react'

import type {
  AuthUser,
  LoginCredentials,
} from '../types/auth'

export interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean

  login: (
    credentials: LoginCredentials,
  ) => Promise<void>

  logout: () => void

  hasPermission: (
    permission: string,
  ) => boolean

  hasAnyPermission: (
    permissions: string[],
  ) => boolean

  hasAllPermissions: (
    permissions: string[],
  ) => boolean
}

export const AuthContext =
  createContext<
    AuthContextValue | undefined
  >(undefined)