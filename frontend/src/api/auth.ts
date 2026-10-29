import apiClient from './client'

import type {
  AuthUser,
  LoginCredentials,
  TokenResponse,
} from '../types/auth'

export async function loginRequest(
  credentials: LoginCredentials,
): Promise<TokenResponse> {
  const body = new URLSearchParams()

  body.set(
    'username',
    credentials.username,
  )

  body.set(
    'password',
    credentials.password,
  )

  body.set(
    'grant_type',
    'password',
  )

  const response =
    await apiClient.post<TokenResponse>(
      '/auth/login',
      body,
      {
        headers: {
          'Content-Type':
            'application/x-www-form-urlencoded',
        },
      },
    )

  return response.data
}

export async function getCurrentUser():
  Promise<AuthUser> {
  const response =
    await apiClient.get<AuthUser>(
      '/auth/me',
    )

  return response.data
}