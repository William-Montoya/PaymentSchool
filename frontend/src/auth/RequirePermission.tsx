import {
  Navigate,
  Outlet,
} from 'react-router-dom'

import {
  useAuth,
} from './useAuth'

import type {
  PermissionName,
} from './permissions'

interface RequirePermissionProps {
  anyOf: readonly PermissionName[]
}

function RequirePermission({
  anyOf,
}: RequirePermissionProps) {
  const {
    hasAnyPermission,
  } = useAuth()

  const allowed =
    hasAnyPermission(
      [...anyOf],
    )

  if (!allowed) {
    return (
      <Navigate
        to="/403"
        replace
      />
    )
  }

  return <Outlet />
}

export default RequirePermission