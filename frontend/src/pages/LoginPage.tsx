import {
  useState,
  type FormEvent,
} from 'react'

import {
  BarChart3,
  Eye,
  EyeOff,
  LockKeyhole,
  TrendingUp,
  UserRound,
} from 'lucide-react'

import {
  useNavigate,
  useSearchParams,
} from 'react-router-dom'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  useAuth,
} from '../auth/useAuth'

function LoginPage() {
  const {
    login,
  } = useAuth()

  const navigate =
    useNavigate()

  const [
    searchParams,
  ] =
    useSearchParams()

  const [
    username,
    setUsername,
  ] =
    useState('')

  const [
    password,
    setPassword,
  ] =
    useState('')

  const [
    showPassword,
    setShowPassword,
  ] =
    useState(false)

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    )

  const [
    isSubmitting,
    setIsSubmitting,
  ] =
    useState(false)

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const normalizedUsername =
      username.trim()

    if (
      !normalizedUsername ||
      !password
    ) {
      setError(
        'Ingrese usuario y contraseña.',
      )
      return
    }

    setError(null)
    setIsSubmitting(true)

    try {
      await login({
        username:
          normalizedUsername,
        password,
      })

      const requested =
        searchParams.get('next')

      const destination =
        requested &&
        requested.startsWith('/') &&
        !requested.startsWith('//')
          ? requested
          : '/'

      navigate(
        destination,
        {
          replace: true,
        },
      )
    } catch (loginError) {
      setError(
        getApiErrorMessage(
          loginError,
          'No fue posible iniciar sesión.',
        ),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-shell">
        <div className="login-form-panel">
          <div className="login-brand">
            <div className="login-brand-mark">
              PS
            </div>

            <div>
              <strong>
                PaymentSchool
              </strong>

              <span>
                Gestión escolar
              </span>
            </div>
          </div>

          <div className="login-content">
            <header className="login-header">
              <span className="eyebrow">
                Bienvenido
              </span>

              <h1>
                Iniciar sesión
              </h1>

              <p>
                Ingrese sus credenciales
                para acceder al sistema.
              </p>
            </header>

            <form
              className="login-form"
              onSubmit={handleSubmit}
            >
              <div className="form-field">
                <label htmlFor="username">
                  Usuario
                </label>

                <div className="input-shell">
                  <UserRound
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    autoFocus
                    value={username}
                    onChange={(event) =>
                      setUsername(
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    placeholder="Ingrese su usuario"
                  />
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="password">
                  Contraseña
                </label>

                <div className="input-shell">
                  <LockKeyhole
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="password"
                    name="password"
                    type={
                      showPassword
                        ? 'text'
                        : 'password'
                    }
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) =>
                      setPassword(
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    placeholder="Ingrese su contraseña"
                  />

                  <button
                    className="password-toggle"
                    type="button"
                    aria-label={
                      showPassword
                        ? (
                          'Ocultar ' +
                          'contraseña'
                        )
                        : (
                          'Mostrar ' +
                          'contraseña'
                        )
                    }
                    onClick={() =>
                      setShowPassword(
                        (current) =>
                          !current,
                      )
                    }
                  >
                    {showPassword ? (
                      <EyeOff
                        size={18}
                        aria-hidden="true"
                      />
                    ) : (
                      <Eye
                        size={18}
                        aria-hidden="true"
                      />
                    )}
                  </button>
                </div>
              </div>

              {error && (
                <div
                  className="form-error"
                  role="alert"
                  aria-live="polite"
                >
                  {error}
                </div>
              )}

              <button
                className={
                  'button ' +
                  'button-primary ' +
                  'button-block ' +
                  'login-submit'
                }
                type="submit"
                disabled={isSubmitting}
              >
                {isSubmitting
                  ? 'Ingresando...'
                  : 'Ingresar'}
              </button>
            </form>
          </div>

          <footer className="login-footer">
            Sistema de Control de Pagos
            Escolares
          </footer>
        </div>

        <div className="login-visual-panel">
          <div
            className="login-glow login-glow-one"
            aria-hidden="true"
          />

          <div
            className="login-glow login-glow-two"
            aria-hidden="true"
          />

          <div className="login-visual-copy">
            <span>
              CONTROL INTEGRAL
            </span>

            <h2>
              Información académica y
              financiera en un solo lugar
            </h2>

            <p>
              Controle pagos, obligaciones,
              solvencias y gestión académica
              desde un panel centralizado.
            </p>
          </div>

          <div className="login-dashboard-preview">
            <div className="preview-header">
              <div>
                <span>
                  Resumen financiero
                </span>

                <strong>
                  Dashboard
                </strong>
              </div>

              <BarChart3
                size={22}
                aria-hidden="true"
              />
            </div>

            <div className="preview-stats">
              <div className="preview-stat">
                <span>
                  Recaudado
                </span>

                <strong>
                  Q 24.8K
                </strong>

                <small>
                  +12.4%
                </small>
              </div>

              <div className="preview-stat">
                <span>
                  Estudiantes
                </span>

                <strong>
                  248
                </strong>

                <small>
                  Activos
                </small>
              </div>
            </div>

            <div className="preview-chart">
              <div className="preview-chart-header">
                <span>
                  Recaudación
                </span>

                <TrendingUp
                  size={17}
                  aria-hidden="true"
                />
              </div>

              <div
                className="preview-bars"
                aria-hidden="true"
              >
                <span
                  style={{
                    height: '36%',
                  }}
                />

                <span
                  style={{
                    height: '58%',
                  }}
                />

                <span
                  style={{
                    height: '43%',
                  }}
                />

                <span
                  style={{
                    height: '78%',
                  }}
                />

                <span
                  style={{
                    height: '64%',
                  }}
                />

                <span
                  style={{
                    height: '92%',
                  }}
                />

                <span
                  style={{
                    height: '72%',
                  }}
                />
              </div>
            </div>

            <div className="preview-bottom">
              <div>
                <span className="preview-dot preview-dot-purple" />

                <small>
                  Pagado
                </small>
              </div>

              <div>
                <span className="preview-dot preview-dot-orange" />

                <small>
                  Pendiente
                </small>
              </div>

              <div className="preview-percentage">
                82%
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default LoginPage