import {
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import type {
  PrecioCarreraCreate,
  TipoPrecio,
} from '../../types/precio'


interface PrecioGradoFormModalProps {
  idCarreraCiclo: number
  idGrado: number
  carreraNombre: string
  gradoNombre: string
  isSubmitting: boolean
  error: string | null

  onClose: () => void

  onSubmit: (
    payload: PrecioCarreraCreate,
  ) => Promise<void>
}


function PrecioGradoFormModal({
  idCarreraCiclo,
  idGrado,
  carreraNombre,
  gradoNombre,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: PrecioGradoFormModalProps) {
  const [
    tipo,
    setTipo,
  ] = useState<TipoPrecio | ''>('')

  const [
    concepto,
    setConcepto,
  ] = useState('')

  const [
    monto,
    setMonto,
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

    if (
      !tipo ||
      !concepto.trim() ||
      !monto ||
      !fechaInicio
    ) {
      return
    }

    await onSubmit({
      id_carrera_ciclo:
        idCarreraCiclo,

      id_grado:
        idGrado,

      tipo,

      concepto:
        concepto.trim(),

      monto:
        monto.trim(),

      fecha_inicio:
        fechaInicio,

      fecha_fin:
        fechaFin ||
        null,
    })
  }

  return (
    <div className="modal-backdrop">
      <div
        className="student-modal academic-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="precio-grado-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Tarifas por grado
            </span>

            <h2 id="precio-grado-title">
              Nueva tarifa
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
                Grado
              </span>

              <input
                type="text"
                value={gradoNombre}
                disabled
              />
            </label>

            <label>
              <span>
                Tipo de tarifa
              </span>

              <select
                value={tipo}
                required
                onChange={(event) =>
                  setTipo(
                    event.target
                      .value as
                      TipoPrecio | '',
                  )
                }
              >
                <option value="">
                  Selecciona un tipo
                </option>

                <option value="INSCRIPCION">
                  Inscripción
                </option>

                <option value="MENSUALIDAD">
                  Mensualidad
                </option>

                <option value="OTRO">
                  Otro
                </option>
              </select>
            </label>

            <label>
              <span>
                Monto
              </span>

              <input
                type="number"
                value={monto}
                min="0"
                step="0.01"
                required
                placeholder="0.00"
                onChange={(event) =>
                  setMonto(
                    event.target.value,
                  )
                }
              />
            </label>

            <label className="student-form-full">
              <span>
                Concepto
              </span>

              <input
                type="text"
                value={concepto}
                maxLength={150}
                required
                placeholder={
                  'Ej. Mensualidad ordinaria'
                }
                onChange={(event) =>
                  setConcepto(
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              <span>
                Vigente desde
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
                Vigente hasta
              </span>

              <input
                type="date"
                value={fechaFin}
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

              <small className="academic-field-help">
                Opcional. Déjalo vacío si
                la tarifa no tiene una fecha
                final definida.
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
                !tipo ||
                !concepto.trim() ||
                !monto ||
                !fechaInicio
              }
            >
              {isSubmitting
                ? 'Guardando...'
                : 'Crear tarifa'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


export default PrecioGradoFormModal