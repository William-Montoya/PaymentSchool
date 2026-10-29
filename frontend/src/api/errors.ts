import axios from 'axios'

interface ValidationDetail {
  msg?: string
}

interface ErrorPayload {
  detail?:
    | string
    | ValidationDetail[]
}

export function getApiErrorMessage(
  error: unknown,
  fallback =
    'Ocurrió un error inesperado.',
): string {
  if (!axios.isAxiosError(error)) {
    return fallback
  }

  if (
    error.code === 'ECONNABORTED'
  ) {
    return (
      'La solicitud tardó demasiado ' +
      'en responder.'
    )
  }

  if (!error.response) {
    return (
      'No fue posible conectar con ' +
      'el servidor.'
    )
  }

  const data =
    error.response.data as
      | ErrorPayload
      | undefined

  const detail = data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => item.msg)
      .filter(
        (message):
          message is string =>
            Boolean(message),
      )

    if (messages.length > 0) {
      return messages.join('. ')
    }
  }

  return fallback
}