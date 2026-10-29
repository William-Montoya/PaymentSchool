import {
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import type {
  CarreraCreate,
} from '../../types/catalogoAcademico'


interface CarreraFormModalProps {
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (
    payload: CarreraCreate,
  ) => Promise<void>
}


function CarreraFormModal({
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: CarreraFormModalProps) {
  const [
    nombre,
    setNombre,
  ] = useState('')

  const [
    descripcion,
    setDescripcion,
  ] = useState('')

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const descripcionNormalizada =
      descripcion.trim()

    await onSubmit({
      nombre: nombre.trim(),
      descripcion:
        descripcionNormalizada ||
        null,
    })
  }

  return (
    <div className="modal-backdrop">
      <div
        className="student-modal academic-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="carrera-form-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Configuración académica
            </span>

            <h2 id="carrera-form-title">
              Nueva carrera
            </h2>
          </div>

          <button
            className="modal-close"
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            aria-label="Cerrar"
          >
            <X
              size={18}
              aria-hidden="true"
            />
          </button>
        </header>

        <form
          className="student-form"
          onSubmit={handleSubmit}
        >
          <div className="student-form-grid">
            <label className="student-form-full">
              <span>
                Nombre de la carrera
              </span>

              <input
                type="text"
                value={nombre}
                maxLength={150}
                required
                placeholder={
                  'Ej. Bachillerato en Computación'
                }
                onChange={(event) =>
                  setNombre(
                    event.target.value,
                  )
                }
              />
            </label>

            <label className="student-form-full">
              <span>
                Descripción
              </span>

              <textarea
                value={descripcion}
                rows={4}
                placeholder={
                  'Descripción opcional de la carrera'
                }
                onChange={(event) =>
                  setDescripcion(
                    event.target.value,
                  )
                }
              />
            </label>
          </div>

          {error && (
            <div className="module-message module-message-error">
              {error}
            </div>
          )}

          <div className="student-modal-actions">
            <button
              className="button button-secondary"
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
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
                : 'Crear carrera'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


export default CarreraFormModal