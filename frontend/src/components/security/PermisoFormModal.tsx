import {
  X,
} from 'lucide-react'

import {
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import type {
  Permiso,
} from '../../types/seguridad'


interface Props {
  permiso: Permiso | null
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (
    nombre: string,
    descripcion: string | null,
  ) => Promise<void>
}


function PermisoFormModal({
  permiso,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [nombre, setNombre] = useState('')
  const [descripcion, setDescripcion] = useState('')

  useEffect(() => {
    setNombre(permiso?.nombre ?? '')
    setDescripcion(permiso?.descripcion ?? '')
  }, [permiso])

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!nombre.trim()) {
      return
    }

    await onSubmit(
      nombre.trim().toUpperCase(),
      descripcion.trim() || null,
    )
  }

  return (
    <div className="security-modal-backdrop" role="presentation">
      <section
        className="security-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="permiso-modal-title"
      >
        <header className="security-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Seguridad
            </span>
            <h2 id="permiso-modal-title">
              {permiso ? 'Editar permiso' : 'Nuevo permiso'}
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
          <label>
            <span>Nombre *</span>
            <input
              value={nombre}
              minLength={3}
              maxLength={150}
              required
              disabled={permiso !== null}
              placeholder="EJEMPLO_VER"
              onChange={(event) => setNombre(event.target.value)}
            />
          </label>

          <label>
            <span>Descripción</span>
            <textarea
              rows={4}
              value={descripcion}
              onChange={(event) => setDescripcion(event.target.value)}
            />
          </label>

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
              disabled={isSubmitting}
            >
              {isSubmitting
                ? 'Guardando...'
                : permiso
                  ? 'Guardar descripción'
                  : 'Crear permiso'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default PermisoFormModal
