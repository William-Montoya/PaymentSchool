import axios from 'axios'

import {
  CheckCircle2,
  Eye,
  FileText,
  FileUp,
  FolderOpen,
} from 'lucide-react'

import {
  useEffect,
  useState,
  type ChangeEvent,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  createExpediente,
  getDocumentoArchivo,
  getExpedienteByEstudiante,
  replaceDocumentoArchivo,
  updateDocumentoEntrega,
  uploadDocumento,
} from '../../api/expedientes'

import {
  getApiErrorMessage,
} from '../../api/errors'

import {
  PERMISSIONS,
} from '../../auth/permissions'

import {
  useAuth,
} from '../../auth/useAuth'

import type {
  EstadoDocumentoExpediente,
  ExpedienteSummary,
} from '../../types/expediente'


interface ExpedienteChecklistProps {
  idEstudiante: number

  onSummaryChange?: (
    summary:
      ExpedienteSummary |
      null,
  ) => void
}


interface EntregaPayload {
  idTipoDocumento: number
  entregado: boolean
}


interface ArchivoPayload {
  documento:
    EstadoDocumentoExpediente
  archivo: File
}


function ExpedienteChecklist({
  idEstudiante,
  onSummaryChange,
}: ExpedienteChecklistProps) {
  const queryClient =
    useQueryClient()

  const {
    hasAnyPermission,
  } = useAuth()

  const canView =
    hasAnyPermission([
      PERMISSIONS.EXPEDIENTES_VER,
    ])

  const canManage =
    hasAnyPermission([
      PERMISSIONS
        .EXPEDIENTES_GESTIONAR,
    ])

  const [
    previewingId,
    setPreviewingId,
  ] = useState<number | null>(
    null,
  )

  const [
    previewError,
    setPreviewError,
  ] = useState<string | null>(
    null,
  )

  const expedienteQuery =
    useQuery({
      queryKey: [
        'expediente-estudiante',
        idEstudiante,
      ],

      queryFn: () =>
        getExpedienteByEstudiante(
          idEstudiante,
        ),

      enabled:
        canView,

      retry: false,
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
      mutationFn:
        createExpediente,

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'expediente-estudiante',
              idEstudiante,
            ],
          })
      },
    })

  const entregaMutation =
    useMutation({
      mutationFn: (
        payload:
          EntregaPayload,
      ) => {
        if (!expedienteQuery.data) {
          throw new Error(
            'Expediente no disponible',
          )
        }

        return updateDocumentoEntrega(
          expedienteQuery
            .data
            .id_expediente,

          payload.idTipoDocumento,

          payload.entregado,
        )
      },

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'expediente-estudiante',
              idEstudiante,
            ],
          })
      },
    })

  const archivoMutation =
    useMutation({
      mutationFn: async (
        payload:
          ArchivoPayload,
      ) => {
        const expediente =
          expedienteQuery.data

        if (!expediente) {
          throw new Error(
            'Expediente no disponible',
          )
        }

        if (
          payload.documento
            .id_documento &&
          payload.documento
            .nombre_archivo
        ) {
          return (
            replaceDocumentoArchivo(
              expediente.id_expediente,

              payload.documento
                .id_documento,

              payload.archivo,
            )
          )
        }

        return uploadDocumento(
          expediente.id_expediente,

          payload.documento
            .id_tipo_documento,

          payload.archivo,
        )
      },

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'expediente-estudiante',
              idEstudiante,
            ],
          })
      },
    })

  useEffect(
    () => {
      const expediente =
        expedienteQuery.data

      if (!expediente) {
        onSummaryChange?.(
          null,
        )

        return
      }

      onSummaryChange?.({
        requeridos:
          expediente
            .documentos_requeridos,

        entregados:
          expediente
            .documentos_entregados,

        pendientes:
          expediente
            .documentos_pendientes,

        completo:
          expediente.completo,
      })
    },
    [
      expedienteQuery.data,
      onSummaryChange,
    ],
  )

  async function handlePreview(
    documento:
      EstadoDocumentoExpediente,
  ) {
    const expediente =
      expedienteQuery.data

    if (
      !expediente ||
      !documento.id_documento ||
      !documento.nombre_archivo
    ) {
      return
    }

    setPreviewError(null)

    setPreviewingId(
      documento.id_documento,
    )

    try {
      const blob =
        await getDocumentoArchivo(
          expediente.id_expediente,
          documento.id_documento,
        )

      const url =
        URL.createObjectURL(
          blob,
        )

      window.open(
        url,
        '_blank',
        'noopener,noreferrer',
      )

      window.setTimeout(
        () =>
          URL.revokeObjectURL(
            url,
          ),
        60000,
      )
    } catch (error) {
      setPreviewError(
        getApiErrorMessage(
          error,
          (
            'No fue posible abrir ' +
            'el archivo.'
          ),
        ),
      )
    } finally {
      setPreviewingId(
        null,
      )
    }
  }

  function handleFileChange(
    documento:
      EstadoDocumentoExpediente,

    event:
      ChangeEvent<HTMLInputElement>,
  ) {
    const archivo =
      event.target
        .files
        ?.[0]

    if (!archivo) {
      return
    }

    archivoMutation.mutate({
      documento,
      archivo,
    })

    event.target.value = ''
  }

  if (!canView) {
    return (
      <div className="enrollment-info-box">
        <FolderOpen
          size={20}
          aria-hidden="true"
        />

        <div>
          <strong>
            Expediente no disponible
          </strong>

          <p>
            Tu usuario no posee permiso
            para consultar expedientes.
            Puedes continuar con la
            inscripción.
          </p>
        </div>
      </div>
    )
  }

  if (
    expedienteQuery.isLoading
  ) {
    return (
      <div className="module-message">
        Cargando expediente...
      </div>
    )
  }

  if (
    expedienteQuery.isError &&
    !isNotFound
  ) {
    return (
      <div className="module-message module-message-error">
        <p>
          {getApiErrorMessage(
            expedienteQuery.error,
            (
              'No fue posible obtener ' +
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
    )
  }

  if (isNotFound) {
    return (
      <div className="enrollment-empty-card">
        <FolderOpen
          size={34}
          aria-hidden="true"
        />

        <strong>
          El estudiante todavía no
          posee expediente
        </strong>

        <p>
          El expediente pertenece al
          estudiante y puede crearse
          ahora antes de finalizar la
          inscripción.
        </p>

        {canManage && (
          <button
            className="button button-primary"
            type="button"
            disabled={
              createMutation.isPending
            }
            onClick={() =>
              createMutation.mutate({
                id_estudiante:
                  idEstudiante,
                observaciones:
                  null,
              })
            }
          >
            {createMutation.isPending
              ? 'Creando...'
              : 'Crear expediente'}
          </button>
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
      </div>
    )
  }

  const expediente =
    expedienteQuery.data

  if (!expediente) {
    return null
  }

  const mutationError =
    entregaMutation.isError
      ? getApiErrorMessage(
          entregaMutation.error,
          (
            'No fue posible cambiar ' +
            'el estado del documento.'
          ),
        )
      : archivoMutation.isError
        ? getApiErrorMessage(
            archivoMutation.error,
            (
              'No fue posible subir ' +
              'el archivo.'
            ),
          )
        : null

  return (
    <div className="expediente-wizard">
      <div className="expediente-summary">
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
            Estado
          </span>

          <strong>
            {expediente.completo
              ? 'Completo'
              : 'Incompleto'}
          </strong>
        </div>
      </div>

      {(mutationError ||
        previewError) && (
        <div className="form-error">
          {mutationError ||
            previewError}
        </div>
      )}

      <div className="expediente-document-list">
        {expediente.documentos.map(
          (documento) => {
            const changingThis =
              entregaMutation
                .isPending &&
              entregaMutation
                .variables
                ?.idTipoDocumento ===
                documento
                  .id_tipo_documento

            const uploadingThis =
              archivoMutation
                .isPending &&
              archivoMutation
                .variables
                ?.documento
                .id_tipo_documento ===
                documento
                  .id_tipo_documento

            return (
              <article
                className="expediente-document-row"
                key={
                  documento
                    .id_tipo_documento
                }
              >
                <div className="expediente-document-main">
                  <label className="expediente-check">
                    <input
                      type="checkbox"
                      checked={
                        documento.entregado
                      }
                      disabled={
                        !canManage ||
                        changingThis
                      }
                      onChange={() =>
                        entregaMutation
                          .mutate({
                            idTipoDocumento:
                              documento
                                .id_tipo_documento,

                            entregado:
                              !documento
                                .entregado,
                          })
                      }
                    />

                    <span className="expediente-check-mark">
                      {documento
                        .entregado && (
                        <CheckCircle2
                          size={16}
                          aria-hidden="true"
                        />
                      )}
                    </span>
                  </label>

                  <div className="expediente-document-copy">
                    <div>
                      <strong>
                        {documento.nombre}
                      </strong>

                      {documento
                        .obligatorio && (
                        <span className="expediente-required">
                          Obligatorio
                        </span>
                      )}
                    </div>

                    <small>
                      {documento.entregado
                        ? 'Entregado'
                        : 'Pendiente'}
                      {' · '}
                      {documento
                        .nombre_archivo
                        ? documento
                            .nombre_archivo
                        : (
                          'Sin archivo ' +
                          'digital'
                        )}
                    </small>
                  </div>
                </div>

                <div className="expediente-document-actions">
                  {documento
                    .nombre_archivo &&
                    documento
                      .id_documento && (
                      <button
                        className="button button-secondary"
                        type="button"
                        disabled={
                          previewingId ===
                          documento
                            .id_documento
                        }
                        onClick={() => {
                          void handlePreview(
                            documento,
                          )
                        }}
                      >
                        <Eye
                          size={15}
                          aria-hidden="true"
                        />

                        {previewingId ===
                        documento
                          .id_documento
                          ? 'Abriendo...'
                          : 'Vista previa'}
                      </button>
                    )}

                  {canManage && (
                    <label
                      className={
                        (
                          'button ' +
                          'button-secondary ' +
                          'expediente-file-button'
                        )
                      }
                    >
                      {documento
                        .nombre_archivo
                        ? (
                          <FileText
                            size={15}
                            aria-hidden="true"
                          />
                        )
                        : (
                          <FileUp
                            size={15}
                            aria-hidden="true"
                          />
                        )}

                      {uploadingThis
                        ? 'Subiendo...'
                        : documento
                            .nombre_archivo
                          ? 'Cambiar'
                          : 'Subir archivo'}

                      <input
                        type="file"
                        accept={
                          (
                            '.pdf,.jpg,.jpeg,' +
                            '.png,application/pdf,' +
                            'image/jpeg,image/png'
                          )
                        }
                        disabled={
                          uploadingThis
                        }
                        onChange={(
                          event,
                        ) =>
                          handleFileChange(
                            documento,
                            event,
                          )
                        }
                      />
                    </label>
                  )}
                </div>
              </article>
            )
          },
        )}
      </div>

      <p className="expediente-note">
        Marcar un documento como entregado
        y almacenar un archivo digital son
        acciones independientes.
      </p>
    </div>
  )
}


export default ExpedienteChecklist