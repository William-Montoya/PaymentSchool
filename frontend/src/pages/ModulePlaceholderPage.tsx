interface ModulePlaceholderPageProps {
  eyebrow: string
  title: string
  description: string
}

function ModulePlaceholderPage({
  eyebrow,
  title,
  description,
}: ModulePlaceholderPageProps) {
  return (
    <main className="page">
      <header className="page-header">
        <div>
          <span className="eyebrow">
            {eyebrow}
          </span>

          <h1>{title}</h1>

          <p>
            {description}
          </p>
        </div>
      </header>

      <section className="card">
        <h2>
          Módulo preparado
        </h2>

        <p className="muted">
          La ruta, el layout y la
          autorización de esta sección
          están funcionando.
        </p>
      </section>
    </main>
  )
}

export default ModulePlaceholderPage