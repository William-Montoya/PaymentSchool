const TOKEN_KEY =
  'paymentschool.access_token'

const EXPIRES_AT_KEY =
  'paymentschool.access_token_expires_at'

export function saveAuthSession(
  token: string,
  expiresInSeconds: number,
): void {
  const expiresAt =
    Date.now() +
    expiresInSeconds * 1000

  sessionStorage.setItem(
    TOKEN_KEY,
    token,
  )

  sessionStorage.setItem(
    EXPIRES_AT_KEY,
    String(expiresAt),
  )
}

export function clearAuthSession(): void {
  sessionStorage.removeItem(
    TOKEN_KEY,
  )

  sessionStorage.removeItem(
    EXPIRES_AT_KEY,
  )
}

export function getTokenExpiresAt():
  number | null {
  const value = sessionStorage.getItem(
    EXPIRES_AT_KEY,
  )

  if (!value) {
    return null
  }

  const expiresAt = Number(value)

  if (!Number.isFinite(expiresAt)) {
    return null
  }

  return expiresAt
}

export function getAccessToken():
  string | null {
  const token = sessionStorage.getItem(
    TOKEN_KEY,
  )

  const expiresAt =
    getTokenExpiresAt()

  if (
    !token ||
    expiresAt === null ||
    expiresAt <= Date.now()
  ) {
    clearAuthSession()
    return null
  }

  return token
}