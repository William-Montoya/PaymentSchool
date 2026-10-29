import {
  Navigate,
  Outlet,
  useLocation,
} from 'react-router-dom'

import FullPageLoader from
  '../components/FullPageLoader'

import {
  useAuth,
} from './useAuth'

function ProtectedRoute() {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth()

  const location =
    useLocation()

  if (isLoading) {
    return (
      <FullPageLoader
        message="Validando sesión..."
      />
    )
  }

  if (!isAuthenticated) {
    const destination =
      location.pathname +
      location.search +
      location.hash

    return (
      <Navigate
        to={
          '/login?next=' +
          encodeURIComponent(
            destination,
          )
        }
        replace
      />
    )
  }

  return <Outlet />
}

export default ProtectedRoute