import {
  Link,
} from 'react-router-dom'

function AccessDeniedPage() {
  return (
    <main className="page page-centered">
      <section className="card not-found">
        <span className="error-code">
          403
        </span>

        <h1>Acceso denegado</h1>

        <p>
          Su usuario no tiene permisos
          para acceder a esta sección.
        </p>

        <Link
          className="button button-primary"
          to="/"
        >
          Volver al inicio
        </Link>
      </section>
    </main>
  )
}

export default AccessDeniedPage