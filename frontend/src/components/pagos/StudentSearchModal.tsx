import {
  Search,
  X,
} from 'lucide-react'

import {
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import {
  getApiErrorMessage,
} from '../../api/errors'

import {
  getInscripcionesFinanzas,
} from '../../api/obligaciones'

import type {
  InscripcionFinanzas,
} from '../../types/obligacion'

export interface PagoStudentSelection {
  id_estudiante: number
  codigo_estudiante: string
  estudiante: string
  inscripciones: InscripcionFinanzas[]
}

interface Props {
  onClose: () => void
  onSelect: (
    selection: PagoStudentSelection,
  ) => void
}

function groupStudents(
  inscripciones: InscripcionFinanzas[],
): PagoStudentSelection[] {
  const map = new Map<number, PagoStudentSelection>()

  for (const inscripcion of inscripciones) {
    const existing = map.get(inscripcion.id_estudiante)

    if (existing) {
      existing.inscripciones.push(inscripcion)
      continue
    }

    map.set(inscripcion.id_estudiante, {
      id_estudiante: inscripcion.id_estudiante,
      codigo_estudiante: inscripcion.codigo_estudiante,
      estudiante: inscripcion.estudiante,
      inscripciones: [inscripcion],
    })
  }

  return Array.from(map.values())
}

function StudentSearchModal({
  onClose,
  onSelect,
}: Props) {
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<InscripcionFinanzas[]>([])

  const students = useMemo(
    () => groupStudents(results),
    [results],
  )

  async function handleSearch(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const term = search.trim()

    if (!term) {
      setResults([])
      setError(null)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const data = await getInscripcionesFinanzas({
        buscar: term,
        limit: 100,
      })

      setResults(data)
    } catch (searchError) {
      setError(
        getApiErrorMessage(
          searchError,
          'No fue posible buscar estudiantes.',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section
        className="student-modal payment-search-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="payment-student-search-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Pagos
            </span>

            <h2 id="payment-student-search-title">
              Buscar estudiante
            </h2>
          </div>

          <button
            className="modal-close"
            type="button"
            aria-label="Cerrar"
            onClick={onClose}
          >
            <X size={19} aria-hidden="true" />
          </button>
        </header>

        <div className="payment-search-modal-body">
          <form
            className="finance-search payment-modal-search"
            onSubmit={handleSearch}
          >
            <Search size={18} aria-hidden="true" />

            <input
              autoFocus
              type="search"
              value={search}
              placeholder="Código, nombre, apellido, CUI..."
              onChange={(event) => setSearch(event.target.value)}
            />

            <button type="submit" disabled={loading}>
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </form>

          {error && (
            <div className="form-error" role="alert">
              {error}
            </div>
          )}

          {!loading && !error && search.trim() && students.length === 0 && (
            <div className="finance-empty payment-modal-empty">
              <Search size={34} aria-hidden="true" />
              <strong>Sin resultados</strong>
              <p>
                No se encontraron estudiantes con inscripciones
                relacionadas con ese criterio.
              </p>
            </div>
          )}

          {students.length > 0 && (
            <div className="module-table-wrapper payment-search-results">
              <table className="module-table">
                <thead>
                  <tr>
                    <th>Carnet</th>
                    <th>Estudiante</th>
                    <th>Última inscripción</th>
                    <th>Acción</th>
                  </tr>
                </thead>

                <tbody>
                  {students.map((student) => {
                    const latest = student.inscripciones[0]

                    return (
                      <tr key={student.id_estudiante}>
                        <td>
                          <strong>{student.codigo_estudiante}</strong>
                        </td>

                        <td>{student.estudiante}</td>

                        <td>
                          <strong>{latest?.ciclo ?? '—'}</strong>
                          <div className="finance-table-secondary">
                            {latest
                              ? `${latest.carrera} · ${latest.grado}`
                              : '—'}
                          </div>
                        </td>

                        <td className="table-action-column">
                          <button
                            className="button button-primary payment-select-student-button"
                            type="button"
                            onClick={() => onSelect(student)}
                          >
                            Seleccionar
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default StudentSearchModal
