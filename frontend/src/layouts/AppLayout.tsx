import {
  LogOut,
  Menu,
  Search,
} from 'lucide-react'

import {
  useState,
} from 'react'

import {
  Outlet,
} from 'react-router-dom'

import {
  useAuth,
} from '../auth/useAuth'

import Sidebar from
  '../components/Sidebar'

const SIDEBAR_STORAGE_KEY =
  'paymentschool.sidebar.collapsed'

function getInitialSidebarState() {
  return (
    localStorage.getItem(
      SIDEBAR_STORAGE_KEY,
    ) === 'true'
  )
}

function AppLayout() {
  const {
    user,
    logout,
  } = useAuth()

  const [
    isSidebarOpen,
    setIsSidebarOpen,
  ] = useState(false)

  const [
    isSidebarCollapsed,
    setIsSidebarCollapsed,
  ] = useState(
    getInitialSidebarState,
  )

  const displayName =
    user?.empleado ??
    user?.username ??
    'Usuario'

  const secondaryText =
    user?.cargo ??
    user?.username ??
    ''

  const initials =
    displayName
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map(
        (part) =>
          part.charAt(0),
      )
      .join('')
      .toUpperCase()

  function handleToggleSidebar() {
    setIsSidebarCollapsed(
      (current) => {
        const next =
          !current

        localStorage.setItem(
          SIDEBAR_STORAGE_KEY,
          String(next),
        )

        return next
      },
    )
  }

  const shellClassName =
    isSidebarCollapsed
      ? (
        'app-shell ' +
        'app-shell-collapsed'
      )
      : 'app-shell'

  return (
    <div
      className={shellClassName}
    >
      <Sidebar
        isOpen={isSidebarOpen}
        collapsed={
          isSidebarCollapsed
        }
        onClose={() =>
          setIsSidebarOpen(false)
        }
        onToggleCollapsed={
          handleToggleSidebar
        }
      />

      <div className="app-main">
        <header className="app-header">
          <div className="header-left">
            <button
              className="menu-button"
              type="button"
              aria-label="Abrir menú"
              onClick={() =>
                setIsSidebarOpen(true)
              }
            >
              <Menu
                size={21}
                aria-hidden="true"
              />
            </button>

            <div className="header-mobile-brand">
              <strong>
                PaymentSchool
              </strong>

              <span>
                Gestión escolar
              </span>
            </div>
          </div>

          <div className="header-search">
            <Search
              size={18}
              aria-hidden="true"
            />

            <input
              type="search"
              aria-label="Buscar"
              placeholder="Buscar en PaymentSchool"
            />

            <span>
              Ctrl K
            </span>
          </div>

          <div className="header-user">
            <div
              className="user-avatar"
              aria-hidden="true"
            >
              {initials || 'U'}
            </div>

            <div className="user-summary">
              <strong>
                {displayName}
              </strong>

              <span>
                {secondaryText}
              </span>
            </div>

            <button
              className="header-logout"
              type="button"
              onClick={logout}
              aria-label="Cerrar sesión"
              title="Cerrar sesión"
            >
              <LogOut
                size={18}
                aria-hidden="true"
              />

              <span>
                Salir
              </span>
            </button>
          </div>
        </header>

        <div className="app-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default AppLayout