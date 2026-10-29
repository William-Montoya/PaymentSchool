import type {
  EstudianteInsolvente,
} from '../../types/reportes'

import {
  formatCurrency,
} from '../../utils/formatters'

interface InsolventStudentsTableProps {
  students: EstudianteInsolvente[]
}

function InsolventStudentsTable({
  students,
}: InsolventStudentsTableProps) {
  return (
    <article className="dashboard-card insolvent-card">
      <header className="dashboard-card-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Seguimiento
          </span>

          <h2>
            Estudiantes insolventes
          </h2>

          <p>
            Estudiantes con saldo
            pendiente registrado.
          </p>
        </div>
      </header>

      {students.length > 0 ? (
        <div className="dashboard-table-wrapper">
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>
                  Código
                </th>

                <th>
                  Estudiante
                </th>

                <th>
                  Grado
                </th>

                <th className="text-right">
                  Deuda
                </th>

                <th>
                  Estado
                </th>
              </tr>
            </thead>

            <tbody>
              {students.map(
                (student) => (
                  <tr
                    key={
                      student.id_inscripcion
                    }
                  >
                    <td>
                      <span className="student-code">
                        {
                          student.codigo_estudiante
                        }
                      </span>
                    </td>

                    <td>
                      <strong>
                        {
                          student.estudiante
                        }
                      </strong>
                    </td>

                    <td>
                      {student.grado}
                    </td>

                    <td className="text-right debt-value">
                      {formatCurrency(
                        student.deuda_total,
                      )}
                    </td>

                    <td>
                      <span className="status-badge status-pending">
                        Pendiente
                      </span>
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="dashboard-empty">
          No hay estudiantes insolventes
          para mostrar.
        </div>
      )}
    </article>
  )
}

export default InsolventStudentsTable