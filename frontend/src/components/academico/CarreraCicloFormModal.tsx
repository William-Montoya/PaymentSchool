import {
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import type {
  Carrera,
  CarreraCicloCreate,
  CicloEscolar,
} from '../../types/catalogoAcademico'


interface CarreraCicloFormModalProps {
  ciclo: CicloEscolar
  carreras: Carrera[]
  isSubmitting: boolean
  error: string | null

  onClose: () => void

  onSubmit: (
    payload: CarreraCicloCreate,
  ) => Promise<void>
}


function CarreraCicloFormModal({
  ciclo,
  carreras,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: CarreraCicloFormModalProps) {
  const [
    idCarrera,
    setIdCarrera,
  ] = useState('')

  const [
    nombreComercial,
    setNombreComercial,
  ] = useState('')

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!idCarrera) {
      return
    }

    const nombreNormalizado =
      nombreComercial.trim()

    await onSubmit({
      id_ciclo:
        ciclo.id_ciclo,

      id_carrera:
        Number(idCarrera),

      nombre_comercial:
        nombreNormalizado ||
        null,
    })
  }

  return (
    <div className="modal-backdrop">
      <div
        className="student-modal academic-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="carrera-ciclo-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Oferta académica
            </span>

            <h2 id="carrera-ciclo-title">
              Agregar carrera al ciclo
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
                Ciclo escolar
              </span>

              <input
                type="text"
                value={ciclo.nombre}
                disabled
              />
            </label>

            <label className="student-form-full">
              <span>
                Carrera
              </span>

              <select
                value={idCarrera}
                required
                onChange={(event) =>
                  setIdCarrera(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Selecciona una carrera
                </option>

                {carreras.map(
                  (carrera) => (
                    <option
                      key={
                        carrera.id_carrera
                      }
                      value={
                        carrera.id_carrera
                      }
                    >
                      {carrera.nombre}
                    </option>
                  ),
                )}
              </select>
            </label>

            <label className="student-form-full">
              <span>
                Nombre comercial
              </span>

              <input
                type="text"
                value={nombreComercial}
                maxLength={150}
                placeholder={
                  'Opcional. Ej. Bachillerato en Computación'
                }
                onChange={(event) =>
                  setNombreComercial(
                    event.target.value,
                  )
                }
              />

              <small className="academic-field-help">
                Puede ser diferente al nombre
                general de la carrera.
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
                !idCarrera
              }
            >
              {isSubmitting
                ? 'Guardando...'
                : 'Agregar carrera'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


export default CarreraCicloFormModal