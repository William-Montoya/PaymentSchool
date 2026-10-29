import {
  Navigate,
  Outlet,
} from 'react-router-dom'

import FullPageLoader from
  '../components/FullPageLoader'

import {
  useAuth,
} from './useAuth'

function PublicOnlyRoute() {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth()

  if (isLoading) {
    return (
      <FullPageLoader
        message="Validando sesión..."
      />
    )
  }

  if (isAuthenticated) {
    return (
      <Navigate
        to="/"
        replace
      />
    )
  }

  return <Outlet />
}

export default PublicOnlyRoute