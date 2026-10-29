import {
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import type {
  CicloCreate,
} from '../../types/catalogoAcademico'


interface CicloFormModalProps {
  isSubmitting: boolean
  error: string | null

  onClose: () => void

  onSubmit: (
    payload: CicloCreate,
  ) => Promise<void>
}


function CicloFormModal({
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: CicloFormModalProps) {
  const [
    nombre,
    setNombre,
  ] = useState('')

  const [
    fechaInicio,
    setFechaInicio,
  ] = useState('')

  const [
    fechaFin,
    setFechaFin,
  ] = useState('')

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    await onSubmit({
      nombre:
        nombre.trim(),

      fecha_inicio:
        fechaInicio,

      fecha_fin:
        fechaFin,

      estado:
        'PLANIFICADO',
    })
  }

  return (
    <div className="modal-backdrop">
      <div
        className="student-modal academic-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="ciclo-form-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Configuración académica
            </span>

            <h2 id="ciclo-form-title">
              Nuevo ciclo escolar
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
                Nombre del ciclo
              </span>

              <input
                type="text"
                value={nombre}
                maxLength={100}
                required
                placeholder="Ej. Ciclo 2027"
                onChange={(event) =>
                  setNombre(
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              <span>
                Fecha de inicio
              </span>

              <input
                type="date"
                value={fechaInicio}
                required
                onChange={(event) =>
                  setFechaInicio(
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              <span>
                Fecha de finalización
              </span>

              <input
                type="date"
                value={fechaFin}
                required
                min={
                  fechaInicio ||
                  undefined
                }
                onChange={(event) =>
                  setFechaFin(
                    event.target.value,
                  )
                }
              />
            </label>
          </div>

          <div className="academic-form-note">
            El nuevo ciclo se registrará
            inicialmente como
            <strong>
              {' '}PLANIFICADO
            </strong>.
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
              disabled={
                isSubmitting ||
                !nombre.trim() ||
                !fechaInicio ||
                !fechaFin
              }
            >
              {isSubmitting
                ? 'Guardando...'
                : 'Crear ciclo'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


export default CicloFormModal