interface FullPageLoaderProps {
  message?: string
}

function FullPageLoader({
  message = 'Cargando...',
}: FullPageLoaderProps) {
  return (
    <main className="loading-screen">
      <div
        className="spinner"
        aria-hidden="true"
      />

      <p>{message}</p>
    </main>
  )
}

export default FullPageLoader