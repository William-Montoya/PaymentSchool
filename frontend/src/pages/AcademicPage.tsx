import {
  CalendarDays,
  GraduationCap,
  Layers3,
  Plus,
} from 'lucide-react'

import {
  useState,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  createCarrera,
  createCiclo,
  getCarreras,
  getCiclos,
} from '../api/catalogoAcademico'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  PERMISSIONS,
} from '../auth/permissions'

import PermissionGate from
  '../auth/PermissionGate'

import CarreraFormModal from
  '../components/academico/CarreraFormModal'

import CicloFormModal from
  '../components/academico/CicloFormModal'

import OfertaAcademicaPanel from
  '../components/academico/OfertaAcademicaPanel'

import type {
  CarreraCreate,
  CicloCreate,
  EstadoCiclo,
} from '../types/catalogoAcademico'

import '../styles/academic.css'


type AcademicTab =
  | 'ciclos'
  | 'carreras'
  | 'oferta'


interface AcademicTabItem {
  id: AcademicTab
  label: string
  description: string
}


const tabs: AcademicTabItem[] = [
  {
    id: 'ciclos',
    label: 'Ciclos',
    description: 'Periodos escolares',
  },
  {
    id: 'carreras',
    label: 'Carreras',
    description: 'Catálogo académico',
  },
  {
    id: 'oferta',
    label: 'Oferta académica',
    description: 'Carreras, grados y tarifas',
  },
]


const estadoCicloLabels:
Record<EstadoCiclo, string> = {
  PLANIFICADO: 'Planificado',
  ACTIVO: 'Activo',
  CERRADO: 'Cerrado',
}


function formatDate(
  value: string,
) {
  const [
    year,
    month,
    day,
  ] = value.split('-')

  if (
    !year ||
    !month ||
    !day
  ) {
    return value
  }

  return `${day}/${month}/${year}`
}


function AcademicPage() {
  const queryClient =
    useQueryClient()

  const [
    activeTab,
    setActiveTab,
  ] = useState<AcademicTab>(
    'oferta',
  )

  const [
    showCreateCiclo,
    setShowCreateCiclo,
  ] = useState(false)

  const [
    showCreateCarrera,
    setShowCreateCarrera,
  ] = useState(false)

  const ciclosQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'ciclos',
      ],

      queryFn:
        getCiclos,

      enabled:
        activeTab === 'ciclos',
    })

  const carrerasQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'carreras',
      ],

      queryFn:
        getCarreras,

      enabled:
        activeTab === 'carreras',
    })

  const createCicloMutation =
    useMutation({
      mutationFn:
        createCiclo,

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'catalogo-academico',
              'ciclos',
            ],
          })

        setShowCreateCiclo(false)
      },
    })

  const createCarreraMutation =
    useMutation({
      mutationFn:
        createCarrera,

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'catalogo-academico',
              'carreras',
            ],
          })

        setShowCreateCarrera(false)
      },
    })

  const ciclos =
    ciclosQuery.data ?? []

  const carreras =
    carrerasQuery.data ?? []

  const ciclosActivos =
    ciclos.filter(
      (ciclo) =>
        ciclo.estado === 'ACTIVO',
    )

  function handleOpenCreateCiclo() {
    createCicloMutation.reset()

    setShowCreateCiclo(true)
  }

  function handleCloseCreateCiclo() {
    createCicloMutation.reset()

    setShowCreateCiclo(false)
  }

  function handleOpenCreateCarrera() {
    createCarreraMutation.reset()

    setShowCreateCarrera(true)
  }

  function handleCloseCreateCarrera() {
    createCarreraMutation.reset()

    setShowCreateCarrera(false)
  }

  async function handleCreateCiclo(
    payload: CicloCreate,
  ) {
    await createCicloMutation
      .mutateAsync(payload)
  }

  async function handleCreateCarrera(
    payload: CarreraCreate,
  ) {
    await createCarreraMutation
      .mutateAsync(payload)
  }

  return (
    <main className="module-page">
      <header className="module-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Gestión académica
          </span>

          <h1>
            Configuración académica
          </h1>

          <p>
            Configura los ciclos escolares,
            carreras, oferta académica, grados
            y tarifas antes de realizar
            inscripciones.
          </p>
        </div>
      </header>

      <section className="academic-tabs-card">
        <div
          className="academic-tabs"
          role="tablist"
          aria-label="Configuración académica"
        >
          {tabs.map((tab) => {
            const Icon =
              tab.id === 'ciclos'
                ? CalendarDays
                : tab.id === 'carreras'
                  ? GraduationCap
                  : Layers3

            const isActive =
              activeTab === tab.id

            return (
              <button
                key={tab.id}
                className={
                  isActive
                    ? (
                      'academic-tab ' +
                      'academic-tab-active'
                    )
                    : 'academic-tab'
                }
                type="button"
                role="tab"
                aria-selected={isActive}
                onClick={() =>
                  setActiveTab(tab.id)
                }
              >
                <span className="academic-tab-icon">
                  <Icon
                    size={19}
                    strokeWidth={1.8}
                    aria-hidden="true"
                  />
                </span>

                <span className="academic-tab-copy">
                  <strong>
                    {tab.label}
                  </strong>

                  <small>
                    {tab.description}
                  </small>
                </span>
              </button>
            )
          })}
        </div>
      </section>

      {activeTab === 'ciclos' && (
        <section className="module-card academic-panel">
          <div className="academic-panel-header">
            <div className="academic-panel-icon">
              <CalendarDays
                size={20}
                strokeWidth={1.8}
                aria-hidden="true"
              />
            </div>

            <div>
              <h2>
                Ciclos escolares
              </h2>

              <p>
                Administra los periodos académicos
                en los que se ofrecerán las
                carreras de la institución.
              </p>
            </div>
          </div>

          <PermissionGate
            anyOf={[
              PERMISSIONS
                .ACADEMICO_GESTIONAR,
            ]}
          >
            <div>
              <button
                className="button button-primary"
                type="button"
                onClick={
                  handleOpenCreateCiclo
                }
              >
                <Plus
                  size={17}
                  aria-hidden="true"
                />

                Nuevo ciclo
              </button>
            </div>
          </PermissionGate>

          {ciclosQuery.isError ? (
            <div className="module-message module-message-error">
              <p>
                {getApiErrorMessage(
                  ciclosQuery.error,
                  'No fue posible cargar los ciclos escolares.',
                )}
              </p>

              <button
                className="button button-secondary"
                type="button"
                onClick={() => {
                  void ciclosQuery.refetch()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : ciclosQuery.isLoading ? (
            <div className="module-message">
              Cargando ciclos escolares...
            </div>
          ) : ciclos.length === 0 ? (
            <div className="academic-empty-state">
              <CalendarDays
                size={34}
                strokeWidth={1.5}
                aria-hidden="true"
              />

              <strong>
                No hay ciclos escolares
              </strong>

              <p>
                Crea el primer ciclo escolar
                para comenzar a configurar
                la oferta académica.
              </p>
            </div>
          ) : (
            <>
              {ciclosActivos.length > 1 && (
                <div className="module-message module-message-error">
                  Se detectó más de un ciclo
                  escolar con estado ACTIVO.
                </div>
              )}

              <div className="module-table-wrapper">
                <table className="module-table">
                  <thead>
                    <tr>
                      <th>
                        Ciclo
                      </th>

                      <th>
                        Fecha de inicio
                      </th>

                      <th>
                        Fecha de finalización
                      </th>

                      <th>
                        Estado
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {ciclos.map(
                      (ciclo) => (
                        <tr
                          key={
                            ciclo.id_ciclo
                          }
                        >
                          <td>
                            <strong>
                              {ciclo.nombre}
                            </strong>
                          </td>

                          <td>
                            {formatDate(
                              ciclo.fecha_inicio,
                            )}
                          </td>

                          <td>
                            {formatDate(
                              ciclo.fecha_fin,
                            )}
                          </td>

                          <td>
                            <strong>
                              {
                                estadoCicloLabels[
                                  ciclo.estado
                                ]
                              }
                            </strong>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      )}

      {activeTab === 'carreras' && (
        <section className="module-card academic-panel">
          <div className="academic-panel-header">
            <div className="academic-panel-icon">
              <GraduationCap
                size={20}
                strokeWidth={1.8}
                aria-hidden="true"
              />
            </div>

            <div>
              <h2>
                Carreras
              </h2>

              <p>
                Mantén el catálogo general de
                carreras disponibles en la
                institución.
              </p>
            </div>
          </div>

          <PermissionGate
            anyOf={[
              PERMISSIONS
                .ACADEMICO_GESTIONAR,
            ]}
          >
            <div>
              <button
                className="button button-primary"
                type="button"
                onClick={
                  handleOpenCreateCarrera
                }
              >
                <Plus
                  size={17}
                  aria-hidden="true"
                />

                Nueva carrera
              </button>
            </div>
          </PermissionGate>

          {carrerasQuery.isError ? (
            <div className="module-message module-message-error">
              <p>
                {getApiErrorMessage(
                  carrerasQuery.error,
                  'No fue posible cargar las carreras.',
                )}
              </p>

              <button
                className="button button-secondary"
                type="button"
                onClick={() => {
                  void carrerasQuery.refetch()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : carrerasQuery.isLoading ? (
            <div className="module-message">
              Cargando carreras...
            </div>
          ) : carreras.length === 0 ? (
            <div className="academic-empty-state">
              <GraduationCap
                size={34}
                strokeWidth={1.5}
                aria-hidden="true"
              />

              <strong>
                No hay carreras registradas
              </strong>

              <p>
                Registra las carreras que la
                institución podrá ofrecer en
                sus distintos ciclos escolares.
              </p>
            </div>
          ) : (
            <div className="module-table-wrapper">
              <table className="module-table">
                <thead>
                  <tr>
                    <th>
                      Carrera
                    </th>

                    <th>
                      Descripción
                    </th>

                    <th>
                      Estado
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {carreras.map(
                    (carrera) => (
                      <tr
                        key={
                          carrera.id_carrera
                        }
                      >
                        <td>
                          <strong>
                            {carrera.nombre}
                          </strong>
                        </td>

                        <td>
                          {
                            carrera.descripcion ??
                            'Sin descripción'
                          }
                        </td>

                        <td>
                          <strong>
                            {carrera.activo
                              ? 'Activa'
                              : 'Inactiva'}
                          </strong>
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

      {activeTab === 'oferta' && (
        <OfertaAcademicaPanel />
      )}

      {showCreateCiclo && (
        <CicloFormModal
          isSubmitting={
            createCicloMutation.isPending
          }
          error={
            createCicloMutation.isError
              ? getApiErrorMessage(
                  createCicloMutation.error,
                  'No fue posible crear el ciclo escolar.',
                )
              : null
          }
          onClose={
            handleCloseCreateCiclo
          }
          onSubmit={
            handleCreateCiclo
          }
        />
      )}

      {showCreateCarrera && (
        <CarreraFormModal
          isSubmitting={
            createCarreraMutation.isPending
          }
          error={
            createCarreraMutation.isError
              ? getApiErrorMessage(
                  createCarreraMutation.error,
                  'No fue posible crear la carrera.',
                )
              : null
          }
          onClose={
            handleCloseCreateCarrera
          }
          onSubmit={
            handleCreateCarrera
          }
        />
      )}
    </main>
  )
}


export default AcademicPage