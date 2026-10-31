import axios from 'axios'

import {
  clearAuthSession,
  getAccessToken,
} from '../auth/storage'

export const AUTH_UNAUTHORIZED_EVENT =
  'paymentschool:unauthorized'

function getApiBaseUrl(): string {
  const configuredUrl =
    import.meta.env.VITE_API_URL?.trim()

  if (!configuredUrl) {
    return '/api'
  }

  const normalizedUrl = configuredUrl.replace(
    /\/+$/,
    '',
  )

  return normalizedUrl.endsWith('/api')
    ? normalizedUrl
    : `${normalizedUrl}/api`
}

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),

  headers: {
    Accept: 'application/json',
  },

  timeout: 15000,
})

apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken()

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`
    }

    return config
  },
)

apiClient.interceptors.response.use(
  (response) => response,

  (error) => {
    const status =
      error.response?.status

    const url =
      error.config?.url ?? ''

    const isLoginRequest =
      url.includes('/auth/login')

    if (
      status === 401 &&
      !isLoginRequest
    ) {
      clearAuthSession()

      if (
        typeof window !== 'undefined'
      ) {
        window.dispatchEvent(
          new Event(
            AUTH_UNAUTHORIZED_EVENT,
          ),
        )
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient