import {
  BadgeDollarSign,
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
  createPrecio,
  getPrecios,
  updatePrecioEstado,
} from '../../api/precios'

import {
  getApiErrorMessage,
} from '../../api/errors'

import {
  PERMISSIONS,
} from '../../auth/permissions'

import PermissionGate from
  '../../auth/PermissionGate'

import type {
  PrecioCarreraCreate,
  TipoPrecio,
} from '../../types/precio'

import PrecioGradoFormModal from
  './PrecioGradoFormModal'


interface TarifasGradoPanelProps {
  idCarreraCiclo: number
  idGrado: number
  carreraNombre: string
  gradoNombre: string
}


interface EstadoMutationPayload {
  idPrecio: number
  activo: boolean
}


const tipoLabels:
Record<TipoPrecio, string> = {
  INSCRIPCION:
    'Inscripción',

  MENSUALIDAD:
    'Mensualidad',

  OTRO:
    'Otro',
}


const moneyFormatter =
  new Intl.NumberFormat(
    'es-GT',
    {
      style: 'currency',
      currency: 'GTQ',
      minimumFractionDigits: 2,
    },
  )


function formatMoney(
  value: string,
) {
  const numericValue =
    Number(value)

  if (
    Number.isNaN(
      numericValue,
    )
  ) {
    return value
  }

  return moneyFormatter.format(
    numericValue,
  )
}


function formatDate(
  value: string | null,
) {
  if (!value) {
    return 'Sin fecha final'
  }

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


function TarifasGradoPanel({
  idCarreraCiclo,
  idGrado,
  carreraNombre,
  gradoNombre,
}: TarifasGradoPanelProps) {
  const queryClient =
    useQueryClient()

  const [
    showCreate,
    setShowCreate,
  ] = useState(false)

  const preciosQuery =
    useQuery({
      queryKey: [
        'precios',
        'grado',
        idGrado,
      ],

      queryFn: () =>
        getPrecios({
          id_carrera_ciclo:
            idCarreraCiclo,

          id_grado:
            idGrado,
        }),
    })

  const createMutation =
    useMutation({
      mutationFn:
        createPrecio,

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'precios',
              'grado',
              idGrado,
            ],
          })

        setShowCreate(false)
      },
    })

  const estadoMutation =
    useMutation({
      mutationFn: (
        payload:
          EstadoMutationPayload,
      ) =>
        updatePrecioEstado(
          payload.idPrecio,
          {
            activo:
              payload.activo,
          },
        ),

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'precios',
              'grado',
              idGrado,
            ],
          })
      },
    })

  const precios =
    preciosQuery.data ?? []

  function handleOpenCreate() {
    createMutation.reset()

    setShowCreate(true)
  }

  function handleCloseCreate() {
    createMutation.reset()

    setShowCreate(false)
  }

  async function handleCreate(
    payload: PrecioCarreraCreate,
  ) {
    await createMutation
      .mutateAsync(payload)
  }

  function handleToggleEstado(
    idPrecio: number,
    activoActual: boolean,
  ) {
    estadoMutation.reset()

    estadoMutation.mutate({
      idPrecio,
      activo:
        !activoActual,
    })
  }

  return (
    <>
      <div className="academic-selected-cycle">
        <div>
          <span>
            Tarifas del grado
          </span>

          <strong>
            {gradoNombre}
          </strong>
        </div>

        <PermissionGate
          anyOf={[
            PERMISSIONS
              .PRECIOS_GESTIONAR,
          ]}
        >
          <button
            className="button button-primary"
            type="button"
            onClick={handleOpenCreate}
          >
            <Plus
              size={17}
              aria-hidden="true"
            />

            Nueva tarifa
          </button>
        </PermissionGate>
      </div>

      {estadoMutation.isError && (
        <div className="module-message module-message-error">
          {getApiErrorMessage(
            estadoMutation.error,
            'No fue posible cambiar el estado de la tarifa.',
          )}
        </div>
      )}

      {preciosQuery.isError ? (
        <div className="module-message module-message-error">
          <p>
            {getApiErrorMessage(
              preciosQuery.error,
              'No fue posible cargar las tarifas del grado.',
            )}
          </p>

          <button
            className="button button-secondary"
            type="button"
            onClick={() => {
              void preciosQuery.refetch()
            }}
          >
            Reintentar
          </button>
        </div>
      ) : preciosQuery.isLoading ? (
        <div className="module-message">
          Cargando tarifas...
        </div>
      ) : precios.length === 0 ? (
        <div className="academic-empty-state">
          <BadgeDollarSign
            size={34}
            strokeWidth={1.5}
            aria-hidden="true"
          />

          <strong>
            No hay tarifas configuradas
          </strong>

          <p>
            Este grado todavía no tiene
            precios de inscripción,
            mensualidad u otros conceptos.
          </p>
        </div>
      ) : (
        <div className="module-table-wrapper">
          <table className="module-table">
            <thead>
              <tr>
                <th>
                  Tipo
                </th>

                <th>
                  Concepto
                </th>

                <th>
                  Monto
                </th>

                <th>
                  Vigencia
                </th>

                <th>
                  Estado
                </th>

                <PermissionGate
                  anyOf={[
                    PERMISSIONS
                      .PRECIOS_GESTIONAR,
                  ]}
                >
                  <th>
                    Acción
                  </th>
                </PermissionGate>
              </tr>
            </thead>

            <tbody>
              {precios.map(
                (precio) => {
                  const changingThis =
                    estadoMutation
                      .isPending &&
                    estadoMutation
                      .variables
                      ?.idPrecio ===
                      precio.id_precio

                  return (
                    <tr
                      key={
                        precio.id_precio
                      }
                    >
                      <td>
                        <strong>
                          {
                            tipoLabels[
                              precio.tipo
                            ]
                          }
                        </strong>
                      </td>

                      <td>
                        {precio.concepto}
                      </td>

                      <td>
                        <strong>
                          {formatMoney(
                            precio.monto,
                          )}
                        </strong>
                      </td>

                      <td>
                        {formatDate(
                          precio.fecha_inicio,
                        )}
                        {' → '}
                        {formatDate(
                          precio.fecha_fin,
                        )}
                      </td>

                      <td>
                        <strong>
                          {precio.activo
                            ? 'Activa'
                            : 'Inactiva'}
                        </strong>
                      </td>

                      <PermissionGate
                        anyOf={[
                          PERMISSIONS
                            .PRECIOS_GESTIONAR,
                        ]}
                      >
                        <td>
                          <button
                            className={
                              precio.activo
                                ? (
                                  'button ' +
                                  'button-secondary'
                                )
                                : (
                                  'button ' +
                                  'button-primary'
                                )
                            }
                            type="button"
                            disabled={
                              changingThis
                            }
                            onClick={() =>
                              handleToggleEstado(
                                precio.id_precio,
                                precio.activo,
                              )
                            }
                          >
                            {changingThis
                              ? 'Guardando...'
                              : precio.activo
                                ? 'Desactivar'
                                : 'Activar'}
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

      {showCreate && (
        <PrecioGradoFormModal
          idCarreraCiclo={
            idCarreraCiclo
          }
          idGrado={
            idGrado
          }
          carreraNombre={
            carreraNombre
          }
          gradoNombre={
            gradoNombre
          }
          isSubmitting={
            createMutation.isPending
          }
          error={
            createMutation.isError
              ? getApiErrorMessage(
                  createMutation.error,
                  'No fue posible crear la tarifa.',
                )
              : null
          }
          onClose={
            handleCloseCreate
          }
          onSubmit={
            handleCreate
          }
        />
      )}
    </>
  )
}


export default TarifasGradoPanel