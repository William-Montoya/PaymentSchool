import {
  X,
} from 'lucide-react'

import {
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import type {
  Empleado,
  RolDetalle,
  UsuarioCreate,
} from '../../types/seguridad'


interface Props {
  empleados: Empleado[]
  roles: RolDetalle[]
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (payload: UsuarioCreate) => Promise<void>
}


function UsuarioFormModal({
  empleados,
  roles,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [idEmpleado, setIdEmpleado] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [idsRol, setIdsRol] = useState<number[]>([])

  const rolesActivos = useMemo(
    () => roles.filter((rol) => rol.activo),
    [roles],
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

    if (
      !idEmpleado ||
      !username.trim() ||
      password.length < 12 ||
      idsRol.length === 0
    ) {
      return
    }

    await onSubmit({
      id_empleado: Number(idEmpleado),
      username: username.trim(),
      password,
      ids_rol: idsRol,
    })
  }

  return (
    <div className="security-modal-backdrop" role="presentation">
      <section
        className="security-modal security-modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="usuario-modal-title"
      >
        <header className="security-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Seguridad
            </span>
            <h2 id="usuario-modal-title">
              Nuevo usuario
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
            <label className="security-form-full">
              <span>Empleado *</span>
              <select
                value={idEmpleado}
                required
                onChange={(event) => setIdEmpleado(event.target.value)}
              >
                <option value="">Selecciona un empleado</option>
                {empleados.map((empleado) => (
                  <option
                    key={empleado.id_empleado}
                    value={empleado.id_empleado}
                  >
                    {empleado.nombres} {empleado.apellidos}
                    {empleado.cargo ? ` — ${empleado.cargo}` : ''}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Usuario *</span>
              <input
                value={username}
                minLength={3}
                maxLength={80}
                required
                autoComplete="off"
                onChange={(event) => setUsername(event.target.value)}
              />
            </label>

            <label>
              <span>Contraseña *</span>
              <input
                type="password"
                value={password}
                minLength={12}
                maxLength={128}
                required
                autoComplete="new-password"
                onChange={(event) => setPassword(event.target.value)}
              />
              <small>Mínimo 12 caracteres.</small>
            </label>
          </div>

          <div className="security-choice-section">
            <div>
              <strong>Roles *</strong>
              <p>Selecciona al menos un rol activo.</p>
            </div>

            <div className="security-choice-grid">
              {rolesActivos.map((rol) => (
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
                    <small>{rol.descripcion ?? 'Sin descripción'}</small>
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
              disabled={isSubmitting || idsRol.length === 0}
            >
              {isSubmitting ? 'Creando...' : 'Crear usuario'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default UsuarioFormModal
