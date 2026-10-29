import {
  useState,
  type FormEvent,
} from 'react'

import {
  X,
} from 'lucide-react'

import type {
  EstadoEstudiante,
  Estudiante,
} from '../../types/estudiante'

interface Props {
  estudiante: Estudiante
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (
    estado: EstadoEstudiante,
  ) => Promise<void>
}

const estados:
  EstadoEstudiante[] = [
    'ACTIVO',
    'INACTIVO',
    'RETIRADO',
    'EGRESADO',
  ]

function EstudianteEstadoModal({
  estudiante,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [
    estado,
    setEstado,
  ] =
    useState<EstadoEstudiante>(
      estudiante.estado,
    )

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    await onSubmit(estado)
  }

  return (
    <div className="modal-backdrop">
      <section
        className="student-modal student-modal-small"
        role="dialog"
        aria-modal="true"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Estado
            </span>

            <h2>
              Cambiar estado
            </h2>
          </div>

          <button
            type="button"
            className="modal-close"
            onClick={onClose}
            aria-label="Cerrar"
          >
            <X
              size={19}
              aria-hidden="true"
            />
          </button>
        </header>

        <form
          className="student-form"
          onSubmit={handleSubmit}
        >
          <p className="student-state-copy">
            {estudiante.nombres}
            {' '}
            {estudiante.apellidos}
          </p>

          <div className="form-field">
            <label htmlFor="estadoEstudiante">
              Estado
            </label>

            <select
              id="estadoEstudiante"
              value={estado}
              onChange={(event) =>
                setEstado(
                  event.target
                    .value as EstadoEstudiante,
                )
              }
            >
              {estados.map(
                (item) => (
                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>
                ),
              )}
            </select>
          </div>

          {error && (
            <div
              className="form-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <footer className="student-modal-actions">
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
                estado === estudiante.estado
              }
            >
              {isSubmitting
                ? 'Actualizando...'
                : 'Actualizar estado'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}

export default EstudianteEstadoModal