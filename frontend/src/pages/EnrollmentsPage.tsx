import {
  ClipboardList,
  Eye,
  UserPlus,
} from 'lucide-react'

import {
  useState,
} from 'react'

import {
  useQuery,
} from '@tanstack/react-query'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  getInscripciones,
} from '../api/inscripciones'

import {
  PERMISSIONS,
} from '../auth/permissions'

import PermissionGate from
  '../auth/PermissionGate'

import InscripcionDetalleModal from
  '../components/inscripciones/InscripcionDetalleModal'

import InscripcionWizard from
  '../components/inscripciones/InscripcionWizard'

import type {
  EstadoInscripcion,
  InscripcionDetalle,
  TipoInscripcion,
} from '../types/inscripcion'

import '../styles/students.css'
import '../styles/enrollments.css'
import '../styles/inscripcion-detail.css'


const tipoLabels:
Record<TipoInscripcion, string> = {
  NUEVA:
    'Nueva',

  REINSCRIPCION:
    'Reinscripción',

  TRASLADO:
    'Traslado',
}


const estadoLabels:
Record<EstadoInscripcion, string> = {
  ACTIVA:
    'Activa',

  FINALIZADA:
    'Finalizada',

  CANCELADA:
    'Cancelada',

  RETIRADA:
    'Retirada',
}


function formatDate(
  value: string,
) {
  return new Intl
    .DateTimeFormat(
      'es-GT',
      {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      },
    )
    .format(
      new Date(
        `${value}T00:00:00`,
      ),
    )
}


function EnrollmentsPage() {
  const [
    showWizard,
    setShowWizard,
  ] = useState(false)

  const [
    selectedInscripcion,
    setSelectedInscripcion,
  ] = useState<
    InscripcionDetalle |
    null
  >(null)

  const inscripcionesQuery =
    useQuery({
      queryKey: [
        'inscripciones',
      ],

      queryFn: () =>
        getInscripciones(),
    })

  const inscripciones =
    inscripcionesQuery.data ??
    []

  return (
    <>
      <main className="module-page">
        <header className="module-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Gestión académica
            </span>

            <h1>
              Inscripciones
            </h1>

            <p>
              Administración de
              inscripciones y expediente
              del estudiante.
            </p>
          </div>

          {!showWizard && (
            <PermissionGate
              anyOf={[
                PERMISSIONS
                  .ACADEMICO_GESTIONAR,
              ]}
            >
              <button
                className="button button-primary"
                type="button"
                onClick={() =>
                  setShowWizard(
                    true,
                  )
                }
              >
                <UserPlus
                  size={17}
                  aria-hidden="true"
                />

                Nueva inscripción
              </button>
            </PermissionGate>
          )}
        </header>

        {showWizard ? (
          <InscripcionWizard
            onClose={() =>
              setShowWizard(
                false,
              )
            }
          />
        ) : (
          <section className="module-card">
            {inscripcionesQuery
              .isError ? (
              <div className="module-message module-message-error">
                <p>
                  {getApiErrorMessage(
                    inscripcionesQuery
                      .error,
                    (
                      'No fue posible cargar ' +
                      'las inscripciones.'
                    ),
                  )}
                </p>

                <button
                  className="button button-secondary"
                  type="button"
                  onClick={() => {
                    void inscripcionesQuery
                      .refetch()
                  }}
                >
                  Reintentar
                </button>
              </div>
            ) : inscripcionesQuery
                .isLoading ? (
              <div className="module-message">
                Cargando inscripciones...
              </div>
            ) : inscripciones.length ===
                0 ? (
              <div className="enrollment-empty-card">
                <ClipboardList
                  size={38}
                  aria-hidden="true"
                />

                <strong>
                  No hay inscripciones
                  registradas
                </strong>

                <p>
                  Crea la primera
                  inscripción para
                  comenzar.
                </p>
              </div>
            ) : (
              <div className="module-table-wrapper">
                <table className="module-table">
                  <thead>
                    <tr>
                      <th>
                        Estudiante
                      </th>

                      <th>
                        Ciclo
                      </th>

                      <th>
                        Carrera
                      </th>

                      <th>
                        Grado
                      </th>

                      <th>
                        Tipo
                      </th>

                      <th>
                        Fecha
                      </th>

                      <th>
                        Estado
                      </th>

                      <th>
                        Acción
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {inscripciones.map(
                      (item) => (
                        <tr
                          key={
                            item
                              .id_inscripcion
                          }
                        >
                          <td>
                            <strong>
                              {
                                item
                                  .estudiante
                              }
                            </strong>

                            <div className="enrollment-table-code">
                              {
                                item
                                  .codigo_estudiante
                              }
                            </div>
                          </td>

                          <td>
                            {item.ciclo}
                          </td>

                          <td>
                            {item.carrera}
                          </td>

                          <td>
                            {item.grado}
                          </td>

                          <td>
                            {
                              tipoLabels[
                                item.tipo
                              ]
                            }
                          </td>

                          <td>
                            {formatDate(
                              item
                                .fecha_inscripcion,
                            )}
                          </td>

                          <td>
                            <span className="enrollment-status">
                              {
                                estadoLabels[
                                  item.estado
                                ]
                              }
                            </span>
                          </td>

                          <td className="table-action-column">
                            <button
                              className="table-icon-button"
                              type="button"
                              title="Ver inscripción"
                              aria-label="Ver inscripción"
                              onClick={() =>
                                setSelectedInscripcion(
                                  item,
                                )
                              }
                            >
                              <Eye
                                size={17}
                                aria-hidden="true"
                              />
                            </button>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}
      </main>

      {selectedInscripcion && (
        <InscripcionDetalleModal
          inscripcion={
            selectedInscripcion
          }
          onClose={() =>
            setSelectedInscripcion(
              null,
            )
          }
        />
      )}
    </>
  )
}


export default EnrollmentsPage