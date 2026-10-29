import {
  X,
} from 'lucide-react'

import {
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import type {
  Empleado,
  EmpleadoCreate,
} from '../../types/seguridad'


interface Props {
  empleado: Empleado | null
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (payload: EmpleadoCreate) => Promise<void>
}


function nullable(value: string): string | null {
  const normalized = value.trim()
  return normalized ? normalized : null
}


function EmpleadoFormModal({
  empleado,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [nombres, setNombres] = useState('')
  const [apellidos, setApellidos] = useState('')
  const [telefono, setTelefono] = useState('')
  const [email, setEmail] = useState('')
  const [cargo, setCargo] = useState('')

  useEffect(() => {
    setNombres(empleado?.nombres ?? '')
    setApellidos(empleado?.apellidos ?? '')
    setTelefono(empleado?.telefono ?? '')
    setEmail(empleado?.email ?? '')
    setCargo(empleado?.cargo ?? '')
  }, [empleado])

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!nombres.trim() || !apellidos.trim()) {
      return
    }

    await onSubmit({
      nombres: nombres.trim(),
      apellidos: apellidos.trim(),
      telefono: nullable(telefono),
      email: nullable(email),
      cargo: nullable(cargo),
    })
  }

  return (
    <div className="security-modal-backdrop" role="presentation">
      <section
        className="security-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="empleado-modal-title"
      >
        <header className="security-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Administración
            </span>
            <h2 id="empleado-modal-title">
              {empleado ? 'Editar empleado' : 'Nuevo empleado'}
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
              <span>Nombres *</span>
              <input
                value={nombres}
                maxLength={100}
                required
                onChange={(event) => setNombres(event.target.value)}
              />
            </label>

            <label>
              <span>Apellidos *</span>
              <input
                value={apellidos}
                maxLength={100}
                required
                onChange={(event) => setApellidos(event.target.value)}
              />
            </label>

            <label>
              <span>Cargo</span>
              <input
                value={cargo}
                maxLength={100}
                onChange={(event) => setCargo(event.target.value)}
              />
            </label>

            <label>
              <span>Teléfono</span>
              <input
                value={telefono}
                maxLength={30}
                onChange={(event) => setTelefono(event.target.value)}
              />
            </label>

            <label className="security-form-full">
              <span>Correo electrónico</span>
              <input
                type="email"
                value={email}
                maxLength={150}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
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
                : empleado
                  ? 'Guardar cambios'
                  : 'Crear empleado'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default EmpleadoFormModal
