import {
  BookOpenCheck,
  Plus,
} from 'lucide-react'

import {
  useMemo,
  useState,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  createCarreraCiclo,
  createGrado,
  getCarreraCiclos,
  getCarreras,
  getCiclos,
  getGrados,
} from '../../api/catalogoAcademico'

import {
  getApiErrorMessage,
} from '../../api/errors'

import {
  PERMISSIONS,
} from '../../auth/permissions'

import PermissionGate from
  '../../auth/PermissionGate'

import type {
  CarreraCicloCreate,
  GradoCreate,
} from '../../types/catalogoAcademico'

import CarreraCicloFormModal from
  './CarreraCicloFormModal'

import GradoFormModal from
  './GradoFormModal'

import TarifasGradoPanel from
  './TarifasGradoPanel'


function OfertaAcademicaPanel() {
  const queryClient =
    useQueryClient()

  const [
    selectedCicloId,
    setSelectedCicloId,
  ] = useState<number | null>(
    null,
  )

  const [
    selectedCarreraCicloId,
    setSelectedCarreraCicloId,
  ] = useState<number | null>(
    null,
  )

  const [
    selectedGradoId,
    setSelectedGradoId,
  ] = useState<number | null>(
    null,
  )

  const [
    showCreateCarreraCiclo,
    setShowCreateCarreraCiclo,
  ] = useState(false)

  const [
    showCreateGrado,
    setShowCreateGrado,
  ] = useState(false)

  const ciclosQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'ciclos',
      ],

      queryFn:
        getCiclos,
    })

  const carrerasQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'carreras',
      ],

      queryFn:
        getCarreras,
    })

  const carreraCiclosQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'carrera-ciclos',
        selectedCicloId,
      ],

      queryFn: () =>
        getCarreraCiclos({
          id_ciclo:
            selectedCicloId ??
            undefined,
        }),

      enabled:
        selectedCicloId !== null,
    })

  const gradosQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'grados',
        selectedCarreraCicloId,
      ],

      queryFn: () =>
        getGrados({
          id_carrera_ciclo:
            selectedCarreraCicloId ??
            undefined,
        }),

      enabled:
        selectedCarreraCicloId !== null,
    })

  const createCarreraCicloMutation =
    useMutation({
      mutationFn:
        createCarreraCiclo,

      onSuccess: async (
        carreraCiclo,
      ) => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'catalogo-academico',
              'carrera-ciclos',
              selectedCicloId,
            ],
          })

        setShowCreateCarreraCiclo(
          false,
        )

        setSelectedCarreraCicloId(
          carreraCiclo.id_carrera_ciclo,
        )

        setSelectedGradoId(null)
      },
    })

  const createGradoMutation =
    useMutation({
      mutationFn:
        createGrado,

      onSuccess: async (
        grado,
      ) => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'catalogo-academico',
              'grados',
              selectedCarreraCicloId,
            ],
          })

        setShowCreateGrado(false)

        setSelectedGradoId(
          grado.id_grado,
        )
      },
    })

  const ciclos =
    ciclosQuery.data ?? []

  const carreras =
    carrerasQuery.data ?? []

  const carreraCiclos =
    carreraCiclosQuery.data ?? []

  const grados =
    gradosQuery.data ?? []

  const selectedCiclo =
    ciclos.find(
      (ciclo) =>
        ciclo.id_ciclo ===
        selectedCicloId,
    ) ?? null

  const selectedCarreraCiclo =
    carreraCiclos.find(
      (item) =>
        item.id_carrera_ciclo ===
        selectedCarreraCicloId,
    ) ?? null

  const selectedGrado =
    grados.find(
      (grado) =>
        grado.id_grado ===
        selectedGradoId,
    ) ?? null

  const carrerasPorId =
    useMemo(
      () =>
        new Map(
          carreras.map(
            (carrera) => [
              carrera.id_carrera,
              carrera,
            ],
          ),
        ),
      [carreras],
    )

  const carrerasDisponibles =
    useMemo(
      () => {
        const asignadas =
          new Set(
            carreraCiclos.map(
              (item) =>
                item.id_carrera,
            ),
          )

        return carreras.filter(
          (carrera) =>
            carrera.activo &&
            !asignadas.has(
              carrera.id_carrera,
            ),
        )
      },
      [
        carreras,
        carreraCiclos,
      ],
    )

  const selectedCarrera =
    selectedCarreraCiclo
      ? (
        carrerasPorId.get(
          selectedCarreraCiclo
            .id_carrera,
        ) ?? null
      )
      : null

  const selectedCarreraNombre =
    selectedCarreraCiclo
      ? (
        selectedCarreraCiclo
          .nombre_comercial ||
        selectedCarrera
          ?.nombre ||
        `Carrera #${selectedCarreraCiclo.id_carrera}`
      )
      : ''

  function handleCicloChange(
    value: string,
  ) {
    setSelectedCicloId(
      value
        ? Number(value)
        : null,
    )

    setSelectedCarreraCicloId(
      null,
    )

    setSelectedGradoId(null)

    setShowCreateCarreraCiclo(
      false,
    )

    setShowCreateGrado(false)
  }

  function handleSelectCarreraCiclo(
    idCarreraCiclo: number,
  ) {
    setSelectedCarreraCicloId(
      idCarreraCiclo,
    )

    setSelectedGradoId(null)

    setShowCreateGrado(false)
  }

  function handleSelectGrado(
    idGrado: number,
  ) {
    setSelectedGradoId(
      idGrado,
    )
  }

  function handleOpenCreateCarreraCiclo() {
    createCarreraCicloMutation
      .reset()

    setShowCreateCarreraCiclo(
      true,
    )
  }

  function handleCloseCreateCarreraCiclo() {
    createCarreraCicloMutation
      .reset()

    setShowCreateCarreraCiclo(
      false,
    )
  }

  function handleOpenCreateGrado() {
    createGradoMutation.reset()

    setShowCreateGrado(true)
  }

  function handleCloseCreateGrado() {
    createGradoMutation.reset()

    setShowCreateGrado(false)
  }

  async function handleCreateCarreraCiclo(
    payload: CarreraCicloCreate,
  ) {
    await createCarreraCicloMutation
      .mutateAsync(payload)
  }

  async function handleCreateGrado(
    payload: GradoCreate,
  ) {
    await createGradoMutation
      .mutateAsync(payload)
  }

  return (
    <>
      <section className="module-card academic-panel">
        <div className="academic-panel-header">
          <div className="academic-panel-icon">
            <BookOpenCheck
              size={20}
              strokeWidth={1.8}
              aria-hidden="true"
            />
          </div>

          <div>
            <h2>
              Oferta académica
            </h2>

            <p>
              Selecciona un ciclo, configura
              sus carreras, grados y tarifas.
            </p>
          </div>
        </div>

        {ciclosQuery.isError ? (
          <div className="module-message module-message-error">
            {getApiErrorMessage(
              ciclosQuery.error,
              'No fue posible cargar los ciclos escolares.',
            )}
          </div>
        ) : ciclosQuery.isLoading ? (
          <div className="module-message">
            Cargando ciclos escolares...
          </div>
        ) : ciclos.length === 0 ? (
          <div className="academic-empty-state">
            <BookOpenCheck
              size={34}
              strokeWidth={1.5}
              aria-hidden="true"
            />

            <strong>
              Primero debes crear un ciclo
            </strong>

            <p>
              La oferta académica siempre
              pertenece a un ciclo escolar.
            </p>
          </div>
        ) : (
          <>
            <div className="academic-offer-toolbar">
              <label className="academic-cycle-selector">
                <span>
                  Ciclo escolar
                </span>

                <select
                  value={
                    selectedCicloId ??
                    ''
                  }
                  onChange={(event) =>
                    handleCicloChange(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Selecciona un ciclo
                  </option>

                  {ciclos.map(
                    (ciclo) => (
                      <option
                        key={
                          ciclo.id_ciclo
                        }
                        value={
                          ciclo.id_ciclo
                        }
                      >
                        {ciclo.nombre}
                        {' — '}
                        {ciclo.estado}
                      </option>
                    ),
                  )}
                </select>
              </label>

              {selectedCiclo && (
                <PermissionGate
                  anyOf={[
                    PERMISSIONS
                      .ACADEMICO_GESTIONAR,
                  ]}
                >
                  <button
                    className="button button-primary"
                    type="button"
                    disabled={
                      carrerasDisponibles
                        .length === 0
                    }
                    onClick={
                      handleOpenCreateCarreraCiclo
                    }
                  >
                    <Plus
                      size={17}
                      aria-hidden="true"
                    />

                    Agregar carrera
                  </button>
                </PermissionGate>
              )}
            </div>

            {!selectedCiclo ? (
              <div className="academic-empty-state">
                <BookOpenCheck
                  size={34}
                  strokeWidth={1.5}
                  aria-hidden="true"
                />

                <strong>
                  Selecciona un ciclo escolar
                </strong>

                <p>
                  Podrás consultar y configurar
                  las carreras ofrecidas en
                  ese ciclo.
                </p>
              </div>
            ) : carrerasQuery.isError ? (
              <div className="module-message module-message-error">
                {getApiErrorMessage(
                  carrerasQuery.error,
                  'No fue posible cargar las carreras.',
                )}
              </div>
            ) : carreraCiclosQuery.isError ? (
              <div className="module-message module-message-error">
                <p>
                  {getApiErrorMessage(
                    carreraCiclosQuery.error,
                    'No fue posible cargar la oferta académica.',
                  )}
                </p>

                <button
                  className="button button-secondary"
                  type="button"
                  onClick={() => {
                    void carreraCiclosQuery
                      .refetch()
                  }}
                >
                  Reintentar
                </button>
              </div>
            ) : (
              <>
                <div className="academic-selected-cycle">
                  <div>
                    <span>
                      Ciclo seleccionado
                    </span>

                    <strong>
                      {selectedCiclo.nombre}
                    </strong>
                  </div>

                  <span className="academic-cycle-state">
                    {selectedCiclo.estado}
                  </span>
                </div>

                {carreraCiclosQuery
                  .isLoading ? (
                  <div className="module-message">
                    Cargando oferta académica...
                  </div>
                ) : carreraCiclos.length === 0 ? (
                  <div className="academic-empty-state">
                    <BookOpenCheck
                      size={34}
                      strokeWidth={1.5}
                      aria-hidden="true"
                    />

                    <strong>
                      El ciclo todavía no tiene
                      carreras asignadas
                    </strong>

                    <p>
                      Agrega una carrera para
                      comenzar a construir la
                      oferta académica del ciclo.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="module-table-wrapper">
                      <table className="module-table">
                        <thead>
                          <tr>
                            <th>
                              Carrera
                            </th>

                            <th>
                              Nombre comercial
                            </th>

                            <th>
                              Estado
                            </th>

                            <th>
                              Grados
                            </th>
                          </tr>
                        </thead>

                        <tbody>
                          {carreraCiclos.map(
                            (item) => {
                              const carrera =
                                carrerasPorId
                                  .get(
                                    item.id_carrera,
                                  )

                              const isSelected =
                                item.id_carrera_ciclo ===
                                selectedCarreraCicloId

                              return (
                                <tr
                                  key={
                                    item.id_carrera_ciclo
                                  }
                                >
                                  <td>
                                    <strong>
                                      {
                                        carrera
                                          ?.nombre ??
                                        `Carrera #${item.id_carrera}`
                                      }
                                    </strong>
                                  </td>

                                  <td>
                                    {
                                      item.nombre_comercial ??
                                      'Mismo nombre de la carrera'
                                    }
                                  </td>

                                  <td>
                                    <strong>
                                      {item.estado
                                        ? 'Activa'
                                        : 'Inactiva'}
                                    </strong>
                                  </td>

                                  <td>
                                    <button
                                      className={
                                        isSelected
                                          ? 'button button-primary'
                                          : 'button button-secondary'
                                      }
                                      type="button"
                                      onClick={() =>
                                        handleSelectCarreraCiclo(
                                          item.id_carrera_ciclo,
                                        )
                                      }
                                    >
                                      {isSelected
                                        ? 'Seleccionada'
                                        : 'Ver grados'}
                                    </button>
                                  </td>
                                </tr>
                              )
                            },
                          )}
                        </tbody>
                      </table>
                    </div>

                    {selectedCarreraCiclo && (
                      <>
                        <div className="academic-selected-cycle">
                          <div>
                            <span>
                              Carrera seleccionada
                            </span>

                            <strong>
                              {selectedCarreraNombre}
                            </strong>
                          </div>

                          <PermissionGate
                            anyOf={[
                              PERMISSIONS
                                .ACADEMICO_GESTIONAR,
                            ]}
                          >
                            <button
                              className="button button-primary"
                              type="button"
                              onClick={
                                handleOpenCreateGrado
                              }
                            >
                              <Plus
                                size={17}
                                aria-hidden="true"
                              />

                              Agregar grado
                            </button>
                          </PermissionGate>
                        </div>

                        {gradosQuery.isError ? (
                          <div className="module-message module-message-error">
                            <p>
                              {getApiErrorMessage(
                                gradosQuery.error,
                                'No fue posible cargar los grados.',
                              )}
                            </p>

                            <button
                              className="button button-secondary"
                              type="button"
                              onClick={() => {
                                void gradosQuery
                                  .refetch()
                              }}
                            >
                              Reintentar
                            </button>
                          </div>
                        ) : gradosQuery.isLoading ? (
                          <div className="module-message">
                            Cargando grados...
                          </div>
                        ) : grados.length === 0 ? (
                          <div className="academic-empty-state">
                            <BookOpenCheck
                              size={34}
                              strokeWidth={1.5}
                              aria-hidden="true"
                            />

                            <strong>
                              No hay grados configurados
                            </strong>

                            <p>
                              Agrega los grados
                              disponibles para esta
                              carrera dentro del ciclo
                              seleccionado.
                            </p>
                          </div>
                        ) : (
                          <div className="module-table-wrapper">
                            <table className="module-table">
                              <thead>
                                <tr>
                                  <th>
                                    Grado
                                  </th>

                                  <th>
                                    Orden
                                  </th>

                                  <th>
                                    Estado
                                  </th>

                                  <PermissionGate
                                    anyOf={[
                                      PERMISSIONS
                                        .FINANZAS_VER,
                                    ]}
                                  >
                                    <th>
                                      Tarifas
                                    </th>
                                  </PermissionGate>
                                </tr>
                              </thead>

                              <tbody>
                                {grados.map(
                                  (grado) => {
                                    const isSelected =
                                      grado.id_grado ===
                                      selectedGradoId

                                    return (
                                      <tr
                                        key={
                                          grado.id_grado
                                        }
                                      >
                                        <td>
                                          <strong>
                                            {grado.nombre}
                                          </strong>
                                        </td>

                                        <td>
                                          {
                                            grado.nivel_orden ??
                                            'Sin orden'
                                          }
                                        </td>

                                        <td>
                                          <strong>
                                            {grado.activo
                                              ? 'Activo'
                                              : 'Inactivo'}
                                          </strong>
                                        </td>

                                        <PermissionGate
                                          anyOf={[
                                            PERMISSIONS
                                              .FINANZAS_VER,
                                          ]}
                                        >
                                          <td>
                                            <button
                                              className={
                                                isSelected
                                                  ? 'button button-primary'
                                                  : 'button button-secondary'
                                              }
                                              type="button"
                                              onClick={() =>
                                                handleSelectGrado(
                                                  grado.id_grado,
                                                )
                                              }
                                            >
                                              {isSelected
                                                ? 'Seleccionado'
                                                : 'Ver tarifas'}
                                            </button>
                                          </td>
                                        </PermissionGate>
                                      </tr>
                                    )
                                  },
                                )}
                              </tbody>
                            </table>
                          </div>
                        )}

                        {selectedGrado && (
                          <PermissionGate
                            anyOf={[
                              PERMISSIONS
                                .FINANZAS_VER,
                            ]}
                          >
                            <TarifasGradoPanel
                              idCarreraCiclo={
                                selectedCarreraCiclo
                                  .id_carrera_ciclo
                              }
                              idGrado={
                                selectedGrado
                                  .id_grado
                              }
                              carreraNombre={
                                selectedCarreraNombre
                              }
                              gradoNombre={
                                selectedGrado.nombre
                              }
                            />
                          </PermissionGate>
                        )}
                      </>
                    )}
                  </>
                )}
              </>
            )}
          </>
        )}
      </section>

      {showCreateCarreraCiclo &&
        selectedCiclo && (
          <CarreraCicloFormModal
            ciclo={selectedCiclo}
            carreras={
              carrerasDisponibles
            }
            isSubmitting={
              createCarreraCicloMutation
                .isPending
            }
            error={
              createCarreraCicloMutation
                .isError
                ? getApiErrorMessage(
                    createCarreraCicloMutation
                      .error,
                    'No fue posible agregar la carrera al ciclo.',
                  )
                : null
            }
            onClose={
              handleCloseCreateCarreraCiclo
            }
            onSubmit={
              handleCreateCarreraCiclo
            }
          />
        )}

      {showCreateGrado &&
        selectedCarreraCiclo && (
          <GradoFormModal
            idCarreraCiclo={
              selectedCarreraCiclo
                .id_carrera_ciclo
            }
            carreraNombre={
              selectedCarreraNombre
            }
            isSubmitting={
              createGradoMutation.isPending
            }
            error={
              createGradoMutation.isError
                ? getApiErrorMessage(
                    createGradoMutation.error,
                    'No fue posible crear el grado.',
                  )
                : null
            }
            onClose={
              handleCloseCreateGrado
            }
            onSubmit={
              handleCreateGrado
            }
          />
        )}
    </>
  )
}


export default OfertaAcademicaPanel