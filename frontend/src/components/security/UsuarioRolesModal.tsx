import {
  X,
} from 'lucide-react'

import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import type {
  RolDetalle,
  UsuarioDetalle,
} from '../../types/seguridad'


interface Props {
  usuario: UsuarioDetalle
  roles: RolDetalle[]
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (idsRol: number[]) => Promise<void>
}


function UsuarioRolesModal({
  usuario,
  roles,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [idsRol, setIdsRol] = useState<number[]>([])

  useEffect(() => {
    setIdsRol(usuario.roles.map((rol) => rol.id_rol))
  }, [usuario])

  const rolesDisponibles = useMemo(
    () => roles.filter(
      (rol) => rol.activo || idsRol.includes(rol.id_rol),
    ),
    [roles, idsRol],
  )

  function toggleRol(idRol: number) {
    setIdsRol((current) =>
      current.includes(idRol)
        ? current.filter((id) => id !== idRol)
        : [...current, idRol],
    )
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (idsRol.length === 0) {
      return
    }

    await onSubmit(idsRol)
  }

  return (
    <div className="security-modal-backdrop" role="presentation">
      <section
        className="security-modal security-modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="usuario-roles-title"
      >
        <header className="security-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              {usuario.username}
            </span>
            <h2 id="usuario-roles-title">
              Roles del usuario
            </h2>
          </div>

          <button
            className="security-icon-button"
            type="button"
            aria-label="Cerrar"
            disabled={isSubmitting}
            onClick={onClose}
          >
            <X size={19} aria-hidden="true" />
          </button>
        </header>

        <form className="security-form" onSubmit={handleSubmit}>
          <div className="security-choice-grid">
            {rolesDisponibles.map((rol) => (
              <label
                className="security-choice-card"
                key={rol.id_rol}
              >
                <input
                  type="checkbox"
                  checked={idsRol.includes(rol.id_rol)}
                  onChange={() => toggleRol(rol.id_rol)}
                />
                <span>
                  <strong>{rol.nombre}</strong>
                  <small>
                    {rol.descripcion ?? 'Sin descripción'}
                    {!rol.activo ? ' · Inactivo' : ''}
                  </small>
                </span>
              </label>
            ))}
          </div>

          {error && (
            <div className="security-error" role="alert">
              {error}
            </div>
          )}

          <footer className="security-modal-actions">
            <button
              className="button button-secondary"
              type="button"
              disabled={isSubmitting}
              onClick={onClose}
            >
              Cancelar
            </button>
            <button
              className="button button-primary"
              type="submit"
              disabled={isSubmitting || idsRol.length === 0}
            >
              {isSubmitting ? 'Guardando...' : 'Guardar roles'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default UsuarioRolesModal
