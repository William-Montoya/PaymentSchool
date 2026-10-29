import axios from 'axios'

import {
  ArrowLeft,
  CheckCircle2,
  FileText,
  FolderOpen,
  Printer,
  Save,
  Search,
  UserRound,
} from 'lucide-react'

import {
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  getContactos,
} from '../api/contactos'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  createExpediente,
  getExpedienteByEstudiante,
  updateExpediente,
} from '../api/expedientes'

import {
  getEstudiantes,
} from '../api/estudiantes'

import {
  PERMISSIONS,
} from '../auth/permissions'

import {
  useAuth,
} from '../auth/useAuth'

import ContactosStep from
  '../components/inscripciones/ContactosStep'

import ExpedienteChecklist from
  '../components/inscripciones/ExpedienteChecklist'

import type {
  Estudiante,
} from '../types/estudiante'

import {
  printExpedienteResumen,
} from '../utils/printExpediente'

import '../styles/students.css'
import '../styles/enrollments.css'
import '../styles/enrollment-wizard-extra.css'
import '../styles/expedientes.css'


function formatDateTime(
  value: string,
) {
  return new Intl
    .DateTimeFormat(
      'es-GT',
      {
        dateStyle:
          'medium',

        timeStyle:
          'short',
      },
    )
    .format(
      new Date(value),
    )
}


function ExpedientesPage() {
  const queryClient =
    useQueryClient()

  const {
    hasAnyPermission,
  } = useAuth()

  const canManage =
    hasAnyPermission([
      PERMISSIONS
        .EXPEDIENTES_GESTIONAR,
    ])

  const [
    searchDraft,
    setSearchDraft,
  ] = useState('')

  const [
    search,
    setSearch,
  ] = useState('')

  const [
    selectedStudent,
    setSelectedStudent,
  ] = useState<
    Estudiante |
    null
  >(null)

  const [
    observacionesDraft,
    setObservacionesDraft,
  ] = useState('')

  const studentsQuery =
    useQuery({
      queryKey: [
        'estudiantes-expedientes',
        search,
      ],

      queryFn: () =>
        getEstudiantes({
          offset: 0,
          limit: 20,

          buscar:
            search ||
            undefined,
        }),
    })

  const expedienteQuery =
    useQuery({
      queryKey: [
        'expediente-estudiante',
        selectedStudent
          ?.id_estudiante,
      ],

      queryFn: () =>
        getExpedienteByEstudiante(
          selectedStudent!
            .id_estudiante,
        ),

      enabled:
        selectedStudent !== null,

      retry: false,
    })

  const contactosQuery =
    useQuery({
      queryKey: [
        'contactos-estudiante',
        selectedStudent
          ?.id_estudiante,
      ],

      queryFn: () =>
        getContactos(
          selectedStudent!
            .id_estudiante,
          true,
        ),

      enabled:
        selectedStudent !== null,
    })

  const isNotFound =
    axios.isAxiosError(
      expedienteQuery.error,
    ) &&
    expedienteQuery
      .error
      .response
      ?.status === 404

  const createMutation =
    useMutation({
      mutationFn: () => {
        if (!selectedStudent) {
          throw new Error(
            'Estudiante no seleccionado',
          )
        }

        return createExpediente({
          id_estudiante:
            selectedStudent
              .id_estudiante,

          observaciones:
            null,
        })
      },

      onSuccess: async () => {
        if (!selectedStudent) {
          return
        }

        await queryClient
          .invalidateQueries({
            queryKey: [
              'expediente-estudiante',
              selectedStudent
                .id_estudiante,
            ],
          })
      },
    })

  const updateMutation =
    useMutation({
      mutationFn: (
        observaciones:
          string |
          null,
      ) => {
        const expediente =
          expedienteQuery.data

        if (!expediente) {
          throw new Error(
            'Expediente no disponible',
          )
        }

        return updateExpediente(
          expediente.id_expediente,
          {
            observaciones,
          },
        )
      },

      onSuccess: async () => {
        if (!selectedStudent) {
          return
        }

        await queryClient
          .invalidateQueries({
            queryKey: [
              'expediente-estudiante',
              selectedStudent
                .id_estudiante,
            ],
          })
      },
    })

  useEffect(
    () => {
      setObservacionesDraft(
        expedienteQuery
          .data
          ?.observaciones ??
        '',
      )
    },
    [
      expedienteQuery
        .data
        ?.id_expediente,

      expedienteQuery
        .data
        ?.observaciones,
    ],
  )

  const students =
    studentsQuery.data ??
    []

  const expediente =
    expedienteQuery.data ??
    null

  const contactos =
    contactosQuery.data ??
    []

  const contactoPrincipal =
    contactos.find(
      (contacto) =>
        contacto.es_principal,
    ) ?? null

  const observationsChanged =
    expediente !== null &&
    (
      expediente
        .observaciones ??
      ''
    ) !==
      observacionesDraft
        .trim()

  function handleSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setSearch(
      searchDraft.trim(),
    )
  }

  function handleSelectStudent(
    student: Estudiante,
  ) {
    setSelectedStudent(
      student,
    )

    setObservacionesDraft(
      '',
    )

    createMutation.reset()
    updateMutation.reset()
  }

  function handleBack() {
    setSelectedStudent(
      null,
    )

    setObservacionesDraft(
      '',
    )

    createMutation.reset()
    updateMutation.reset()
  }

  function handleSaveObservations() {
    updateMutation.mutate(
      observacionesDraft
        .trim() ||
      null,
    )
  }

  function handlePrint() {
    if (
      !selectedStudent ||
      !expediente
    ) {
      return
    }

    printExpedienteResumen({
      estudiante:
        selectedStudent,

      expediente,

      contactoPrincipal,
    })
  }

  if (!selectedStudent) {
    return (
      <main className="module-page">
        <header className="module-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Gestión académica
            </span>

            <h1>
              Expedientes
            </h1>

            <p>
              Consulta y administración
              de documentación y
              encargados del estudiante.
            </p>
          </div>
        </header>

        <section className="module-card expediente-search-card">
          <header className="expediente-search-header">
            <div>
              <FolderOpen
                size={21}
                aria-hidden="true"
              />

              <div>
                <h2>
                  Buscar estudiante
                </h2>

                <p>
                  Busca por código,
                  nombre, apellido o CUI.
                </p>
              </div>
            </div>
          </header>

          <form
            className="expediente-search-form"
            onSubmit={handleSearch}
          >
            <Search
              size={18}
              aria-hidden="true"
            />

            <input
              type="search"
              value={
                searchDraft
              }
              placeholder={
                (
                  'Código, carnet, ' +
                  'nombre, apellido o CUI...'
                )
              }
              onChange={(event) =>
                setSearchDraft(
                  event.target.value,
                )
              }
            />

            <button
              type="submit"
            >
              Buscar
            </button>
          </form>

          {studentsQuery.isError ? (
            <div className="module-message module-message-error">
              <p>
                {getApiErrorMessage(
                  studentsQuery.error,
                  (
                    'No fue posible cargar ' +
                    'los estudiantes.'
                  ),
                )}
              </p>

              <button
                className="button button-secondary"
                type="button"
                onClick={() => {
                  void studentsQuery
                    .refetch()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : studentsQuery
              .isLoading ? (
            <div className="module-message">
              Cargando estudiantes...
            </div>
          ) : students.length === 0 ? (
            <div className="enrollment-empty-card">
              <UserRound
                size={36}
                aria-hidden="true"
              />

              <strong>
                No se encontraron
                estudiantes
              </strong>

              <p>
                Prueba con otro código,
                nombre, apellido o CUI.
              </p>
            </div>
          ) : (
            <div className="expediente-student-results">
              {students.map(
                (student) => (
                  <button
                    className="expediente-student-result"
                    type="button"
                    key={
                      student
                        .id_estudiante
                    }
                    onClick={() =>
                      handleSelectStudent(
                        student,
                      )
                    }
                  >
                    <span className="expediente-student-avatar">
                      {student.nombres
                        .charAt(0)
                        .toUpperCase()}

                      {student.apellidos
                        .charAt(0)
                        .toUpperCase()}
                    </span>

                    <span className="expediente-student-result-copy">
                      <strong>
                        {student.nombres}
                        {' '}
                        {student.apellidos}
                      </strong>

                      <small>
                        {
                          student
                            .codigo_estudiante
                        }
                        {' · '}
                        {student.cui ||
                          'Sin CUI'}
                      </small>
                    </span>

                    <span
                      className={
                        (
                          'expediente-student-state ' +
                          (
                            student.estado ===
                            'ACTIVO'
                              ? 'expediente-student-state-active'
                              : ''
                          )
                        )
                      }
                    >
                      {student.estado}
                    </span>
                  </button>
                ),
              )}
            </div>
          )}
        </section>
      </main>
    )
  }

  return (
    <main className="module-page">
      <header className="module-header">
        <div>
          <button
            className="expediente-back-button"
            type="button"
            onClick={
              handleBack
            }
          >
            <ArrowLeft
              size={15}
              aria-hidden="true"
            />

            Volver a búsqueda
          </button>

          <span className="dashboard-card-eyebrow">
            Expediente estudiantil
          </span>

          <h1>
            {selectedStudent.nombres}
            {' '}
            {selectedStudent.apellidos}
          </h1>

          <p>
            {
              selectedStudent
                .codigo_estudiante
            }
            {' · '}
            {selectedStudent.estado}
          </p>
        </div>

        {expediente && (
          <button
            className="button button-secondary"
            type="button"
            disabled={
              contactosQuery
                .isLoading
            }
            onClick={
              handlePrint
            }
          >
            <Printer
              size={16}
              aria-hidden="true"
            />

            Imprimir expediente
          </button>
        )}
      </header>

      <section className="expediente-student-summary">
        <article className="module-card">
          <span>
            Código / Carnet
          </span>

          <strong>
            {
              selectedStudent
                .codigo_estudiante
            }
          </strong>
        </article>

        <article className="module-card">
          <span>
            CUI
          </span>

          <strong>
            {selectedStudent.cui ||
              'No registrado'}
          </strong>
        </article>

        <article className="module-card">
          <span>
            Teléfono
          </span>

          <strong>
            {selectedStudent
              .telefono ||
              'No registrado'}
          </strong>
        </article>

        <article className="module-card">
          <span>
            Estado
          </span>

          <strong>
            {
              selectedStudent
                .estado
            }
          </strong>
        </article>
      </section>

      {expedienteQuery.isLoading ? (
        <section className="module-card">
          <div className="module-message">
            Cargando expediente...
          </div>
        </section>
      ) : expedienteQuery.isError &&
          !isNotFound ? (
        <section className="module-card">
          <div className="module-message module-message-error">
            <p>
              {getApiErrorMessage(
                expedienteQuery.error,
                (
                  'No fue posible cargar ' +
                  'el expediente.'
                ),
              )}
            </p>

            <button
              className="button button-secondary"
              type="button"
              onClick={() => {
                void expedienteQuery
                  .refetch()
              }}
            >
              Reintentar
            </button>
          </div>
        </section>
      ) : isNotFound ? (
        <section className="module-card expediente-create-card">
          <FolderOpen
            size={42}
            aria-hidden="true"
          />

          <strong>
            El estudiante aún no posee
            expediente
          </strong>

          <p>
            Puedes crear su expediente
            para comenzar a registrar
            documentación y observaciones.
          </p>

          {canManage ? (
            <button
              className="button button-primary"
              type="button"
              disabled={
                createMutation.isPending
              }
              onClick={() =>
                createMutation.mutate()
              }
            >
              <FileText
                size={16}
                aria-hidden="true"
              />

              {createMutation.isPending
                ? 'Creando...'
                : 'Crear expediente'}
            </button>
          ) : (
            <div className="enrollment-info-box">
              Tu usuario puede consultar
              expedientes, pero no posee
              permiso para crear uno.
            </div>
          )}

          {createMutation.isError && (
            <div className="form-error">
              {getApiErrorMessage(
                createMutation.error,
                (
                  'No fue posible crear ' +
                  'el expediente.'
                ),
              )}
            </div>
          )}
        </section>
      ) : expediente ? (
        <>
          <section className="module-card expediente-overview-card">
            <header className="expediente-section-title">
              <div>
                <CheckCircle2
                  size={20}
                  aria-hidden="true"
                />

                <div>
                  <h2>
                    Estado del expediente
                  </h2>

                  <p>
                    Información general
                    del registro.
                  </p>
                </div>
              </div>

              <span
                className={
                  expediente.completo
                    ? (
                      'expediente-complete-badge'
                    )
                    : (
                      'expediente-incomplete-badge'
                    )
                }
              >
                {expediente.completo
                  ? 'Completo'
                  : 'Incompleto'}
              </span>
            </header>

            <div className="expediente-overview-grid">
              <div>
                <span>
                  Requeridos
                </span>

                <strong>
                  {
                    expediente
                      .documentos_requeridos
                  }
                </strong>
              </div>

              <div>
                <span>
                  Entregados
                </span>

                <strong>
                  {
                    expediente
                      .documentos_entregados
                  }
                </strong>
              </div>

              <div>
                <span>
                  Pendientes
                </span>

                <strong>
                  {
                    expediente
                      .documentos_pendientes
                  }
                </strong>
              </div>

              <div>
                <span>
                  Creado
                </span>

                <strong>
                  {formatDateTime(
                    expediente
                      .creado_en,
                  )}
                </strong>
              </div>
            </div>
          </section>

          <section className="module-card">
            <header className="expediente-section-title">
              <div>
                <FileText
                  size={20}
                  aria-hidden="true"
                />

                <div>
                  <h2>
                    Documentación
                  </h2>

                  <p>
                    Control de documentos
                    entregados y archivos
                    digitalizados.
                  </p>
                </div>
              </div>
            </header>

            <ExpedienteChecklist
              idEstudiante={
                selectedStudent
                  .id_estudiante
              }
            />
          </section>

          <section className="module-card">
            <header className="expediente-section-title">
              <div>
                <FileText
                  size={20}
                  aria-hidden="true"
                />

                <div>
                  <h2>
                    Observaciones
                  </h2>

                  <p>
                    Notas generales del
                    expediente.
                  </p>
                </div>
              </div>
            </header>

            <div className="expediente-observations">
              <label htmlFor="expediente-observaciones">
                Observaciones del expediente
              </label>

              <textarea
                id="expediente-observaciones"
                rows={5}
                value={
                  observacionesDraft
                }
                readOnly={
                  !canManage
                }
                placeholder={
                  (
                    'Agrega notas relacionadas ' +
                    'con la documentación del estudiante.'
                  )
                }
                onChange={(event) =>
                  setObservacionesDraft(
                    event.target.value,
                  )
                }
              />

              {canManage && (
                <div className="expediente-observation-actions">
                  <button
                    className="button button-primary"
                    type="button"
                    disabled={
                      !observationsChanged ||
                      updateMutation
                        .isPending
                    }
                    onClick={
                      handleSaveObservations
                    }
                  >
                    <Save
                      size={15}
                      aria-hidden="true"
                    />

                    {updateMutation.isPending
                      ? 'Guardando...'
                      : 'Guardar observaciones'}
                  </button>
                </div>
              )}

              {updateMutation.isError && (
                <div className="form-error">
                  {getApiErrorMessage(
                    updateMutation.error,
                    (
                      'No fue posible guardar ' +
                      'las observaciones.'
                    ),
                  )}
                </div>
              )}
            </div>
          </section>

          <section className="module-card">
            <header className="expediente-section-title">
              <div>
                <UserRound
                  size={20}
                  aria-hidden="true"
                />

                <div>
                  <h2>
                    Encargados y contactos
                  </h2>

                  <p>
                    Personas responsables
                    asociadas al estudiante.
                  </p>
                </div>
              </div>
            </header>

            <ContactosStep
              idEstudiante={
                selectedStudent
                  .id_estudiante
              }
            />
          </section>
        </>
      ) : null}
    </main>
  )
}


export default ExpedientesPage