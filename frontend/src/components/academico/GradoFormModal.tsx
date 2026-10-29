import {
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import type {
  GradoCreate,
} from '../../types/catalogoAcademico'


interface GradoFormModalProps {
  idCarreraCiclo: number
  carreraNombre: string
  isSubmitting: boolean
  error: string | null

  onClose: () => void

  onSubmit: (
    payload: GradoCreate,
  ) => Promise<void>
}


function GradoFormModal({
  idCarreraCiclo,
  carreraNombre,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: GradoFormModalProps) {
  const [
    nombre,
    setNombre,
  ] = useState('')

  const [
    nivelOrden,
    setNivelOrden,
  ] = useState('')

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const nombreNormalizado =
      nombre.trim()

    if (!nombreNormalizado) {
      return
    }

    await onSubmit({
      id_carrera_ciclo:
        idCarreraCiclo,

      nombre:
        nombreNormalizado,

      nivel_orden:
        nivelOrden
          ? Number(nivelOrden)
          : null,
    })
  }

  return (
    <div className="modal-backdrop">
      <div
        className="student-modal academic-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="grado-form-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Oferta académica
            </span>

            <h2 id="grado-form-title">
              Nuevo grado
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
                Carrera
              </span>

              <input
                type="text"
                value={carreraNombre}
                disabled
              />
            </label>

            <label className="student-form-full">
              <span>
                Nombre del grado
              </span>

              <input
                type="text"
                value={nombre}
                maxLength={100}
                required
                placeholder="Ej. Cuarto"
                onChange={(event) =>
                  setNombre(
                    event.target.value,
                  )
                }
              />
            </label>

            <label className="student-form-full">
              <span>
                Orden académico
              </span>

              <input
                type="number"
                value={nivelOrden}
                min={1}
                step={1}
                placeholder="Ej. 1"
                onChange={(event) =>
                  setNivelOrden(
                    event.target.value,
                  )
                }
              />

              <small className="academic-field-help">
                Opcional. Permite definir el
                orden en que se mostrarán los
                grados de esta carrera.
              </small>
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
              disabled={
                isSubmitting ||
                !nombre.trim()
              }
            >
              {isSubmitting
                ? 'Guardando...'
                : 'Crear grado'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


export default GradoFormModal