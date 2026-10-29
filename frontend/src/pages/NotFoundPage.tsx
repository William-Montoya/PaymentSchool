import { Link } from 'react-router-dom'

function NotFoundPage() {
  return (
    <main className="page page-centered">
      <section className="card not-found">
        <span className="error-code">
          404
        </span>

        <h1>Página no encontrada</h1>

        <p>
          La ruta solicitada no existe.
        </p>

        <Link
          className="button"
          to="/"
        >
          Volver al inicio
        </Link>
      </section>
    </main>
  )
}

export default NotFoundPage