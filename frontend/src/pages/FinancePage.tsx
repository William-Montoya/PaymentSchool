import {
  ArrowLeft,
  CalendarDays,
  Eye,
  FilePlus,
  Plus,
  Search,
  WalletCards,
} from 'lucide-react'

import {
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  createObligacionDesdePrecio,
  createObligacionManual,
  generarMensualidades,
  getInscripcionesFinanzas,
  getObligaciones,
} from '../api/obligaciones'

import {
  getPrecios,
} from '../api/precios'

import {
  PERMISSIONS,
} from '../auth/permissions'

import {
  useAuth,
} from '../auth/useAuth'

import ObligacionDetailModal from
  '../components/finanzas/ObligacionDetailModal'

import ObligacionFormModal from
  '../components/finanzas/ObligacionFormModal'

import type {
  EstadoObligacion,
  InscripcionFinanzas,
  ObligacionCreateAction,
  ObligacionCreateMode,
  ObligacionSaldo,
  TipoObligacion,
} from '../types/obligacion'

import '../styles/students.css'
import '../styles/finances.css'


const estadoLabels:
Record<EstadoObligacion, string> = {
  PENDIENTE:
    'Pendiente',

  PARCIAL:
    'Parcial',

  PAGADA:
    'Pagada',

  ANULADA:
    'Anulada',
}


const tipoLabels:
Record<TipoObligacion, string> = {
  INSCRIPCION:
    'Inscripción',

  MENSUALIDAD:
    'Mensualidad',

  CERTIFICACION:
    'Certificación',

  CONSTANCIA:
    'Constancia',

  OTRO:
    'Otro',
}


function formatMoney(
  value:
    string |
    number,
) {
  return (
    new Intl.NumberFormat(
      'es-GT',
      {
        style: 'currency',
        currency: 'GTQ',
      },
    )
    .format(
      Number(value),
    )
  )
}


function formatDate(
  value:
    string |
    null,
) {
  if (!value) {
    return '—'
  }

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


function FinancePage() {
  const queryClient =
    useQueryClient()

  const {
    hasAnyPermission,
  } = useAuth()

  const canManage =
    hasAnyPermission([
      PERMISSIONS
        .OBLIGACIONES_GESTIONAR,
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
    selectedInscripcion,
    setSelectedInscripcion,
  ] = useState<
    InscripcionFinanzas |
    null
  >(null)

  const [
    estadoFilter,
    setEstadoFilter,
  ] = useState<
    EstadoObligacion |
    ''
  >('')

  const [
    tipoFilter,
    setTipoFilter,
  ] = useState<
    TipoObligacion |
    ''
  >('')

  const [
    createMode,
    setCreateMode,
  ] = useState<
    ObligacionCreateMode |
    null
  >(null)

  const [
    selectedObligacion,
    setSelectedObligacion,
  ] = useState<
    ObligacionSaldo |
    null
  >(null)

  const [
    successMessage,
    setSuccessMessage,
  ] = useState<
    string |
    null
  >(null)

  const inscripcionesQuery =
    useQuery({
      queryKey: [
        'finanzas-inscripciones',
        search,
      ],

      queryFn: () =>
        getInscripcionesFinanzas({
          buscar:
            search ||
            undefined,

          limit: 50,
        }),
    })

  const obligacionesQuery =
    useQuery({
      queryKey: [
        'obligaciones-inscripcion',
        selectedInscripcion
          ?.id_inscripcion,
      ],

      queryFn: () =>
        getObligaciones({
          id_inscripcion:
            selectedInscripcion!
              .id_inscripcion,
        }),

      enabled:
        selectedInscripcion !==
        null,
    })

  const preciosQuery =
    useQuery({
      queryKey: [
        'precios-obligacion',
        selectedInscripcion
          ?.id_carrera_ciclo,
        selectedInscripcion
          ?.id_grado,
      ],

      queryFn: () =>
        getPrecios({
          id_carrera_ciclo:
            selectedInscripcion!
              .id_carrera_ciclo,

          id_grado:
            selectedInscripcion!
              .id_grado,

          activo: true,
        }),

      enabled:
        Boolean(
          selectedInscripcion &&
          selectedInscripcion
            .estado === 'ACTIVA' &&
          canManage,
        ),
    })

  const actionMutation =
    useMutation({
      mutationFn:
        async (
          action:
            ObligacionCreateAction,
        ) => {
          if (
            action.mode ===
            'DESDE_PRECIO'
          ) {
            return (
              createObligacionDesdePrecio(
                action.payload,
              )
            )
          }

          if (
            action.mode ===
            'MENSUALIDADES'
          ) {
            return (
              generarMensualidades(
                action.payload,
              )
            )
          }

          return (
            createObligacionManual(
              action.payload,
            )
          )
        },

      onSuccess:
        async (
          _data,
          action,
        ) => {
          if (
            selectedInscripcion
          ) {
            await queryClient
              .invalidateQueries({
                queryKey: [
                  'obligaciones-inscripcion',
                  selectedInscripcion
                    .id_inscripcion,
                ],
              })
          }

          setCreateMode(
            null,
          )

          if (
            action.mode ===
            'MENSUALIDADES'
          ) {
            setSuccessMessage(
              'Mensualidades generadas correctamente.',
            )

            return
          }

          setSuccessMessage(
            'Obligación creada correctamente.',
          )
        },
    })

  const inscripciones =
    inscripcionesQuery.data ??
    []

  const obligaciones =
    obligacionesQuery.data ??
    []

  const obligacionesFiltradas =
    useMemo(
      () =>
        obligaciones.filter(
          (obligacion) => {
            if (
              estadoFilter &&
              obligacion.estado !==
                estadoFilter
            ) {
              return false
            }

            if (
              tipoFilter &&
              obligacion
                .tipo_obligacion !==
                tipoFilter
            ) {
              return false
            }

            return true
          },
        ),
      [
        obligaciones,
        estadoFilter,
        tipoFilter,
      ],
    )

  const resumen =
    useMemo(
      () =>
        obligaciones.reduce(
          (
            current,
            obligacion,
          ) => ({
            neto:
              current.neto +
              Number(
                obligacion
                  .monto_neto,
              ),

            pagado:
              current.pagado +
              Number(
                obligacion
                  .total_pagado,
              ),

            saldo:
              current.saldo +
              Number(
                obligacion.saldo,
              ),

            abiertas:
              current.abiertas +
              (
                obligacion.estado ===
                  'PENDIENTE' ||
                obligacion.estado ===
                  'PARCIAL'
                  ? 1
                  : 0
              ),
          }),
          {
            neto: 0,
            pagado: 0,
            saldo: 0,
            abiertas: 0,
          },
        ),
      [
        obligaciones,
      ],
    )

  function handleSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setSearch(
      searchDraft.trim(),
    )
  }

  function selectInscripcion(
    inscripcion:
      InscripcionFinanzas,
  ) {
    setSelectedInscripcion(
      inscripcion,
    )

    setEstadoFilter('')
    setTipoFilter('')

    setSuccessMessage(
      null,
    )

    setSelectedObligacion(
      null,
    )
  }

  function goBack() {
    setSelectedInscripcion(
      null,
    )

    setEstadoFilter('')
    setTipoFilter('')

    setSuccessMessage(
      null,
    )
  }

  function openCreate(
    mode:
      ObligacionCreateMode,
  ) {
    actionMutation.reset()

    setSuccessMessage(
      null,
    )

    setCreateMode(
      mode,
    )
  }

  function closeCreate() {
    if (
      actionMutation.isPending
    ) {
      return
    }

    actionMutation.reset()

    setCreateMode(
      null,
    )
  }

  async function handleCreate(
    action:
      ObligacionCreateAction,
  ) {
    await actionMutation
      .mutateAsync(
        action,
      )
  }

  const pricesError =
    preciosQuery.isError
      ? getApiErrorMessage(
          preciosQuery.error,
          (
            'No fue posible cargar ' +
            'las tarifas.'
          ),
        )
      : null

  return (
    <>
      <main className="module-page">
        <header className="module-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Finanzas
            </span>

            <h1>
              Obligaciones
            </h1>

            <p>
              Generación y control de
              cargos financieros por
              inscripción.
            </p>
          </div>

          {selectedInscripcion && (
            <button
              className="button button-secondary"
              type="button"
              onClick={goBack}
            >
              <ArrowLeft
                size={16}
                aria-hidden="true"
              />

              Buscar otra inscripción
            </button>
          )}
        </header>

        {!selectedInscripcion ? (
          <section className="module-card">
            <div className="finance-search-heading">
              <div>
                <h2>
                  Buscar inscripción
                </h2>

                <p>
                  Busca por carnet,
                  estudiante, CUI,
                  carrera, ciclo o grado.
                </p>
              </div>
            </div>

            <form
              className="finance-search"
              onSubmit={
                handleSearch
              }
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
                    'Código, estudiante, ' +
                    'CUI, carrera...'
                  )
                }
                onChange={(event) =>
                  setSearchDraft(
                    event.target
                      .value,
                  )
                }
              />

              <button type="submit">
                Buscar
              </button>
            </form>

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
              <div className="finance-empty">
                <WalletCards
                  size={38}
                  aria-hidden="true"
                />

                <strong>
                  No se encontraron
                  inscripciones
                </strong>

                <p>
                  Intenta con otro criterio
                  de búsqueda.
                </p>
              </div>
            ) : (
              <div className="module-table-wrapper">
                <table className="module-table">
                  <thead>
                    <tr>
                      <th>
                        Carnet
                      </th>

                      <th>
                        Estudiante
                      </th>

                      <th>
                        Ciclo
                      </th>

                      <th>
                        Carrera / Grado
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
                      (inscripcion) => (
                        <tr
                          key={
                            inscripcion
                              .id_inscripcion
                          }
                        >
                          <td>
                            <strong>
                              {
                                inscripcion
                                  .codigo_estudiante
                              }
                            </strong>
                          </td>

                          <td>
                            {
                              inscripcion
                                .estudiante
                            }
                          </td>

                          <td>
                            {
                              inscripcion
                                .ciclo
                            }
                          </td>

                          <td>
                            <strong>
                              {
                                inscripcion
                                  .carrera
                              }
                            </strong>

                            <div className="finance-table-secondary">
                              {
                                inscripcion
                                  .grado
                              }
                            </div>
                          </td>

                          <td>
                            <span
                              className={
                                (
                                  'finance-inscription-status ' +
                                  (
                                    inscripcion
                                      .estado ===
                                    'ACTIVA'
                                      ? 'finance-inscription-active'
                                      : ''
                                  )
                                )
                              }
                            >
                              {
                                inscripcion
                                  .estado
                              }
                            </span>
                          </td>

                          <td className="table-action-column">
                            <button
                              className="table-icon-button"
                              type="button"
                              title="Ver obligaciones"
                              aria-label="Ver obligaciones"
                              onClick={() =>
                                selectInscripcion(
                                  inscripcion,
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
        ) : (
          <div className="finance-content">
            <section className="module-card finance-student-card">
              <div className="finance-student-main">
                <div className="finance-avatar">
                  {
                    selectedInscripcion
                      .estudiante
                      .charAt(0)
                      .toUpperCase()
                  }
                </div>

                <div>
                  <span className="dashboard-card-eyebrow">
                    {
                      selectedInscripcion
                        .codigo_estudiante
                    }
                  </span>

                  <h2>
                    {
                      selectedInscripcion
                        .estudiante
                    }
                  </h2>

                  <p>
                    {
                      selectedInscripcion
                        .ciclo
                    }
                    {' · '}
                    {
                      selectedInscripcion
                        .carrera
                    }
                    {' · '}
                    {
                      selectedInscripcion
                        .grado
                    }
                  </p>
                </div>
              </div>

              <span
                className={
                  (
                    'finance-inscription-status ' +
                    (
                      selectedInscripcion
                        .estado ===
                      'ACTIVA'
                        ? 'finance-inscription-active'
                        : ''
                    )
                  )
                }
              >
                {
                  selectedInscripcion
                    .estado
                }
              </span>
            </section>

            <section className="finance-summary-grid">
              <article className="module-card">
                <span>
                  Monto neto
                </span>

                <strong>
                  {formatMoney(
                    resumen.neto,
                  )}
                </strong>
              </article>

              <article className="module-card">
                <span>
                  Total pagado
                </span>

                <strong>
                  {formatMoney(
                    resumen.pagado,
                  )}
                </strong>
              </article>

              <article className="module-card">
                <span>
                  Saldo pendiente
                </span>

                <strong>
                  {formatMoney(
                    resumen.saldo,
                  )}
                </strong>
              </article>

              <article className="module-card">
                <span>
                  Obligaciones abiertas
                </span>

                <strong>
                  {
                    resumen
                      .abiertas
                  }
                </strong>
              </article>
            </section>

            {successMessage && (
              <div className="finance-success-box">
                {successMessage}
              </div>
            )}

            {selectedInscripcion
              .estado !==
                'ACTIVA' && (
              <div className="finance-info-box">
                Esta inscripción es
                histórica. Puedes consultar
                sus obligaciones, pero el
                backend solo permite generar
                nuevas obligaciones para
                inscripciones activas.
              </div>
            )}

            <section className="module-card">
              <header className="finance-section-header">
                <div>
                  <h2>
                    Obligaciones
                  </h2>

                  <p>
                    Consulta de cargos,
                    pagos aplicados y saldo.
                  </p>
                </div>

                {canManage &&
                  selectedInscripcion
                    .estado ===
                    'ACTIVA' && (
                  <div className="finance-action-buttons">
                    <button
                      className="button button-secondary"
                      type="button"
                      onClick={() =>
                        openCreate(
                          'DESDE_PRECIO',
                        )
                      }
                    >
                      <FilePlus
                        size={16}
                        aria-hidden="true"
                      />

                      Desde tarifa
                    </button>

                    <button
                      className="button button-secondary"
                      type="button"
                      onClick={() =>
                        openCreate(
                          'MENSUALIDADES',
                        )
                      }
                    >
                      <CalendarDays
                        size={16}
                        aria-hidden="true"
                      />

                      Mensualidades
                    </button>

                    <button
                      className="button button-primary"
                      type="button"
                      onClick={() =>
                        openCreate(
                          'MANUAL',
                        )
                      }
                    >
                      <Plus
                        size={16}
                        aria-hidden="true"
                      />

                      Obligación manual
                    </button>
                  </div>
                )}
              </header>

              <div className="finance-filters">
                <label>
                  <span>
                    Estado
                  </span>

                  <select
                    value={
                      estadoFilter
                    }
                    onChange={(event) =>
                      setEstadoFilter(
                        event.target
                          .value as
                          EstadoObligacion |
                          '',
                      )
                    }
                  >
                    <option value="">
                      Todos
                    </option>

                    {Object.entries(
                      estadoLabels,
                    ).map(
                      ([
                        value,
                        label,
                      ]) => (
                        <option
                          key={value}
                          value={value}
                        >
                          {label}
                        </option>
                      ),
                    )}
                  </select>
                </label>

                <label>
                  <span>
                    Tipo
                  </span>

                  <select
                    value={
                      tipoFilter
                    }
                    onChange={(event) =>
                      setTipoFilter(
                        event.target
                          .value as
                          TipoObligacion |
                          '',
                      )
                    }
                  >
                    <option value="">
                      Todos
                    </option>

                    {Object.entries(
                      tipoLabels,
                    ).map(
                      ([
                        value,
                        label,
                      ]) => (
                        <option
                          key={value}
                          value={value}
                        >
                          {label}
                        </option>
                      ),
                    )}
                  </select>
                </label>
              </div>

              {obligacionesQuery
                .isError ? (
                <div className="module-message module-message-error">
                  <p>
                    {getApiErrorMessage(
                      obligacionesQuery
                        .error,
                      (
                        'No fue posible cargar ' +
                        'las obligaciones.'
                      ),
                    )}
                  </p>

                  <button
                    className="button button-secondary"
                    type="button"
                    onClick={() => {
                      void obligacionesQuery
                        .refetch()
                    }}
                  >
                    Reintentar
                  </button>
                </div>
              ) : obligacionesQuery
                  .isLoading ? (
                <div className="module-message">
                  Cargando obligaciones...
                </div>
              ) : obligacionesFiltradas
                  .length === 0 ? (
                <div className="finance-empty">
                  <WalletCards
                    size={36}
                    aria-hidden="true"
                  />

                  <strong>
                    No hay obligaciones
                  </strong>

                  <p>
                    No existen obligaciones
                    para los filtros
                    seleccionados.
                  </p>
                </div>
              ) : (
                <div className="module-table-wrapper">
                  <table className="module-table">
                    <thead>
                      <tr>
                        <th>
                          Concepto
                        </th>

                        <th>
                          Período
                        </th>

                        <th>
                          Vencimiento
                        </th>

                        <th>
                          Neto
                        </th>

                        <th>
                          Pagado
                        </th>

                        <th>
                          Saldo
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
                      {obligacionesFiltradas
                        .map(
                          (obligacion) => (
                            <tr
                              key={
                                obligacion
                                  .id_obligacion
                              }
                            >
                              <td>
                                <strong>
                                  {
                                    obligacion
                                      .concepto
                                  }
                                </strong>

                                <div className="finance-table-secondary">
                                  {
                                    tipoLabels[
                                      obligacion
                                        .tipo_obligacion
                                    ]
                                  }
                                </div>
                              </td>

                              <td>
                                {
                                  obligacion
                                    .periodo ??
                                  '—'
                                }
                              </td>

                              <td>
                                {formatDate(
                                  obligacion
                                    .fecha_vencimiento,
                                )}
                              </td>

                              <td>
                                {formatMoney(
                                  obligacion
                                    .monto_neto,
                                )}
                              </td>

                              <td>
                                {formatMoney(
                                  obligacion
                                    .total_pagado,
                                )}
                              </td>

                              <td>
                                <strong>
                                  {formatMoney(
                                    obligacion
                                      .saldo,
                                  )}
                                </strong>
                              </td>

                              <td>
                                <span
                                  className={
                                    (
                                      'finance-obligation-status ' +
                                      `finance-obligation-${obligacion.estado.toLowerCase()}`
                                    )
                                  }
                                >
                                  {
                                    estadoLabels[
                                      obligacion
                                        .estado
                                    ]
                                  }
                                </span>
                              </td>

                              <td className="table-action-column">
                                <button
                                  className="table-icon-button"
                                  type="button"
                                  title="Ver obligación"
                                  aria-label="Ver obligación"
                                  onClick={() =>
                                    setSelectedObligacion(
                                      obligacion,
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
          </div>
        )}
      </main>

      {createMode &&
        selectedInscripcion && (
          <ObligacionFormModal
            mode={
              createMode
            }
            inscripcion={
              selectedInscripcion
            }
            precios={
              preciosQuery.data ??
              []
            }
            pricesLoading={
              preciosQuery
                .isLoading
            }
            catalogError={
              pricesError
            }
            isSubmitting={
              actionMutation
                .isPending
            }
            error={
              actionMutation
                .isError
                ? getApiErrorMessage(
                    actionMutation
                      .error,
                    (
                      'No fue posible ' +
                      'procesar la obligación.'
                    ),
                  )
                : null
            }
            onClose={
              closeCreate
            }
            onSubmit={
              handleCreate
            }
          />
        )}

      {selectedObligacion && (
        <ObligacionDetailModal
          obligacion={
            selectedObligacion
          }
          onClose={() =>
            setSelectedObligacion(
              null,
            )
          }
        />
      )}
    </>
  )
}


export default FinancePage