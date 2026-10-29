import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import {
  useQueryClient,
} from '@tanstack/react-query'

import {
  getCurrentUser,
  loginRequest,
} from '../api/auth'

import {
  AUTH_UNAUTHORIZED_EVENT,
} from '../api/client'

import {
  AuthContext,
} from './authContext'

import {
  clearAuthSession,
  getAccessToken,
  getTokenExpiresAt,
  saveAuthSession,
} from './storage'

import type {
  AuthUser,
  LoginCredentials,
} from '../types/auth'

interface AuthProviderProps {
  children: ReactNode
}

function AuthProvider({
  children,
}: AuthProviderProps) {
  const queryClient =
    useQueryClient()

  const [
    user,
    setUser,
  ] =
    useState<AuthUser | null>(
      null,
    )

  const [
    isLoading,
    setIsLoading,
  ] =
    useState(true)

  const clearAuthenticatedState =
    useCallback(() => {
      clearAuthSession()
      setUser(null)
      queryClient.clear()
    }, [queryClient])

  useEffect(() => {
    let active = true

    async function bootstrap() {
      const token =
        getAccessToken()

      if (!token) {
        if (active) {
          setIsLoading(false)
        }

        return
      }

      try {
        const currentUser =
          await getCurrentUser()

        if (active) {
          setUser(currentUser)
        }
      } catch {
        clearAuthSession()

        if (active) {
          setUser(null)
        }
      } finally {
        if (active) {
          setIsLoading(false)
        }
      }
    }

    void bootstrap()

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    const handleUnauthorized = () => {
      clearAuthenticatedState()
    }

    window.addEventListener(
      AUTH_UNAUTHORIZED_EVENT,
      handleUnauthorized,
    )

    return () => {
      window.removeEventListener(
        AUTH_UNAUTHORIZED_EVENT,
        handleUnauthorized,
      )
    }
  }, [clearAuthenticatedState])

  useEffect(() => {
    if (!user) {
      return
    }

    const expiresAt =
      getTokenExpiresAt()

    const remaining =
      expiresAt === null
        ? 0
        : Math.max(
            0,
            expiresAt - Date.now(),
          )

    const timer =
      window.setTimeout(
        clearAuthenticatedState,
        remaining,
      )

    return () => {
      window.clearTimeout(timer)
    }
  }, [
    user,
    clearAuthenticatedState,
  ])

  const login = useCallback(
    async (
      credentials:
        LoginCredentials,
    ) => {
      try {
        const token =
          await loginRequest(
            credentials,
          )

        saveAuthSession(
          token.access_token,
          token.expires_in,
        )

        const currentUser =
          await getCurrentUser()

        setUser(currentUser)
      } catch (error) {
        clearAuthSession()
        setUser(null)
        throw error
      }
    },
    [],
  )

  const logout = useCallback(() => {
    clearAuthenticatedState()
  }, [clearAuthenticatedState])

  const permissionSet =
    useMemo(
      () =>
        new Set(
          user?.permisos.map(
            (permission) =>
              permission.nombre,
          ) ?? [],
        ),
      [user],
    )

  const hasPermission =
    useCallback(
      (permission: string) =>
        permissionSet.has(
          permission,
        ),
      [permissionSet],
    )

  const hasAnyPermission =
    useCallback(
      (permissions: string[]) =>
        permissions.some(
          (permission) =>
            permissionSet.has(
              permission,
            ),
        ),
      [permissionSet],
    )

  const hasAllPermissions =
    useCallback(
      (permissions: string[]) =>
        permissions.every(
          (permission) =>
            permissionSet.has(
              permission,
            ),
        ),
      [permissionSet],
    )

  const value =
    useMemo(
      () => ({
        user,
        isAuthenticated:
          user !== null,
        isLoading,
        login,
        logout,
        hasPermission,
        hasAnyPermission,
        hasAllPermissions,
      }),
      [
        user,
        isLoading,
        login,
        logout,
        hasPermission,
        hasAnyPermission,
        hasAllPermissions,
      ],
    )

  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  )
}

export default AuthProvider