import type {
  ReactNode,
} from 'react'

import {
  useAuth,
} from './useAuth'

import type {
  PermissionName,
} from './permissions'

interface PermissionGateProps {
  anyOf?: readonly PermissionName[]
  allOf?: readonly PermissionName[]
  fallback?: ReactNode
  children: ReactNode
}

function PermissionGate({
  anyOf,
  allOf,
  fallback = null,
  children,
}: PermissionGateProps) {
  const {
    hasAnyPermission,
    hasAllPermissions,
  } = useAuth()

  const passesAny =
    !anyOf ||
    anyOf.length === 0 ||
    hasAnyPermission(
      [...anyOf],
    )

  const passesAll =
    !allOf ||
    allOf.length === 0 ||
    hasAllPermissions(
      [...allOf],
    )

  if (
    !passesAny ||
    !passesAll
  ) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

export default PermissionGate