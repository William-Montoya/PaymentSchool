import {
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react'

import {
  NavLink,
} from 'react-router-dom'

import {
  useAuth,
} from '../auth/useAuth'

import {
  navigationSections,
} from '../routes/navigation'

interface SidebarProps {
  isOpen: boolean
  collapsed: boolean
  onClose: () => void
  onToggleCollapsed: () => void
}

function Sidebar({
  isOpen,
  collapsed,
  onClose,
  onToggleCollapsed,
}: SidebarProps) {
  const {
    hasAnyPermission,
  } = useAuth()

  function canSeeItem(
    permissions?: readonly string[],
  ) {
    if (
      !permissions ||
      permissions.length === 0
    ) {
      return true
    }

    return hasAnyPermission(
      [...permissions],
    )
  }

  const sidebarClassName = [
    'sidebar',
    isOpen
      ? 'sidebar-open'
      : '',
    collapsed
      ? 'sidebar-collapsed'
      : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <>
      <aside
        className={sidebarClassName}
      >
        <div className="sidebar-brand">
          <div className="brand-mark">
            PS
          </div>

          <div className="brand-copy">
            <strong>
              PaymentSchool
            </strong>

            <span>
              Gestión escolar
            </span>
          </div>
        </div>

        <nav
          className="sidebar-nav"
          aria-label="Navegación principal"
        >
          {navigationSections.map(
            (section) => {
              const visibleItems =
                section.items.filter(
                  (item) =>
                    canSeeItem(
                      item.permissions,
                    ),
                )

              if (
                visibleItems.length === 0
              ) {
                return null
              }

              return (
                <section
                  className="nav-section"
                  key={section.label}
                >
                  <span
                    className="nav-section-title"
                  >
                    {section.label}
                  </span>

                  <div className="nav-items">
                    {visibleItems.map(
                      (item) => {
                        const Icon =
                          item.icon

                        return (
                          <NavLink
                            key={item.path}
                            to={item.path}
                            end={
                              item.path ===
                              '/'
                            }
                            onClick={
                              onClose
                            }
                            title={
                              collapsed
                                ? item.label
                                : undefined
                            }
                            aria-label={
                              item.label
                            }
                            className={({
                              isActive,
                            }) =>
                              isActive
                                ? (
                                  'nav-link ' +
                                  'nav-link-active'
                                )
                                : 'nav-link'
                            }
                          >
                            <span
                              className="nav-icon"
                            >
                              <Icon
                                size={19}
                                strokeWidth={1.8}
                                aria-hidden="true"
                              />
                            </span>

                            <span
                              className="nav-label"
                            >
                              {item.label}
                            </span>
                          </NavLink>
                        )
                      },
                    )}
                  </div>
                </section>
              )
            },
          )}
        </nav>

        <div className="sidebar-footer">
          <button
            className="sidebar-collapse-button"
            type="button"
            onClick={
              onToggleCollapsed
            }
            title={
              collapsed
                ? 'Expandir menú'
                : 'Contraer menú'
            }
            aria-label={
              collapsed
                ? 'Expandir menú'
                : 'Contraer menú'
            }
          >
            {collapsed ? (
              <PanelLeftOpen
                size={19}
                aria-hidden="true"
              />
            ) : (
              <PanelLeftClose
                size={19}
                aria-hidden="true"
              />
            )}

            <span>
              {collapsed
                ? ''
                : 'Contraer menú'}
            </span>
          </button>
        </div>
      </aside>

      {isOpen && (
        <button
          className="sidebar-overlay"
          type="button"
          aria-label="Cerrar menú"
          onClick={onClose}
        />
      )}
    </>
  )
}

export default Sidebar