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
  RolDetalle,
} from '../../types/seguridad'


interface RolFormResult {
  nombre: string
  descripcion: string | null
  idsPermiso: number[]
}


interface Props {
  rol: RolDetalle | null
  permisos: Permiso[]
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (data: RolFormResult) => Promise<void>
}


function RolFormModal({
  rol,
  permisos,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [nombre, setNombre] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [idsPermiso, setIdsPermiso] = useState<number[]>([])

  useEffect(() => {
    setNombre(rol?.nombre ?? '')
    setDescripcion(rol?.descripcion ?? '')
    setIdsPermiso(rol?.permisos.map((item) => item.id_permiso) ?? [])
  }, [rol])

  function togglePermiso(idPermiso: number) {
    setIdsPermiso((current) =>
      current.includes(idPermiso)
        ? current.filter((id) => id !== idPermiso)
        : [...current, idPermiso],
    )
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!nombre.trim()) {
      return
    }

    await onSubmit({
      nombre: nombre.trim().toUpperCase(),
      descripcion: descripcion.trim() || null,
      idsPermiso,
    })
  }

  return (
    <div className="security-modal-backdrop" role="presentation">
      <section
        className="security-modal security-modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="rol-modal-title"
      >
        <header className="security-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Seguridad
            </span>
            <h2 id="rol-modal-title">
              {rol ? 'Editar rol' : 'Nuevo rol'}
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
          <div className="security-form-grid">
            <label>
              <span>Nombre *</span>
              <input
                value={nombre}
                minLength={2}
                maxLength={100}
                required
                disabled={rol !== null}
                onChange={(event) => setNombre(event.target.value)}
              />
            </label>

            <label className="security-form-full">
              <span>Descripción</span>
              <textarea
                rows={3}
                value={descripcion}
                onChange={(event) => setDescripcion(event.target.value)}
              />
            </label>
          </div>

          <div className="security-choice-section">
            <div>
              <strong>Permisos del rol</strong>
              <p>Los permisos seleccionados reemplazan la asignación actual.</p>
            </div>

            <div className="security-permissions-grid">
              {permisos.map((permiso) => (
                <label
                  className="security-choice-card"
                  key={permiso.id_permiso}
                >
                  <input
                    type="checkbox"
                    checked={idsPermiso.includes(permiso.id_permiso)}
                    onChange={() => togglePermiso(permiso.id_permiso)}
                  />
                  <span>
                    <strong>{permiso.nombre}</strong>
                    <small>{permiso.descripcion ?? 'Sin descripción'}</small>
                  </span>
                </label>
              ))}
            </div>
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
              disabled={isSubmitting}
            >
              {isSubmitting
                ? 'Guardando...'
                : rol
                  ? 'Guardar cambios'
                  : 'Crear rol'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default RolFormModal
