import {
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'


interface Props {
  username: string
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (password: string) => Promise<void>
}


function PasswordModal({
  username,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [password, setPassword] = useState('')
  const [confirmacion, setConfirmacion] = useState('')

  const mismatch =
    confirmacion.length > 0 && password !== confirmacion

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (
      password.length < 12 ||
      password !== confirmacion
    ) {
      return
    }

    await onSubmit(password)
  }

  return (
    <div className="security-modal-backdrop" role="presentation">
      <section
        className="security-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="password-modal-title"
      >
        <header className="security-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              {username}
            </span>
            <h2 id="password-modal-title">
              Cambiar contraseña
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
            <span>Nueva contraseña *</span>
            <input
              type="password"
              minLength={12}
              maxLength={128}
              required
              value={password}
              autoComplete="new-password"
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          <label>
            <span>Confirmar contraseña *</span>
            <input
              type="password"
              minLength={12}
              maxLength={128}
              required
              value={confirmacion}
              autoComplete="new-password"
              onChange={(event) => setConfirmacion(event.target.value)}
            />
          </label>

          {mismatch && (
            <div className="security-error">
              Las contraseñas no coinciden.
            </div>
          )}

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
              disabled={
                isSubmitting ||
                password.length < 12 ||
                password !== confirmacion
              }
            >
              {isSubmitting ? 'Actualizando...' : 'Cambiar contraseña'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default PasswordModal
