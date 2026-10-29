import {
  AlertTriangle,
  Bell,
  CheckCircle2,
  Clock,
  Eye,
  Plus,
  Search,
  Users,
  X,
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
  buscarContactosNotificacion,
  createAvisoDeuda,
  createNotificacion,
  getNotificacion,
  getNotificaciones,
  marcarDestinatarioAbierto,
} from '../api/notificaciones'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  PERMISSIONS,
} from '../auth/permissions'

import {
  useAuth,
} from '../auth/useAuth'

import type {
  EstadoDestinatario,
  NotificacionContacto,
} from '../types/notificacion'

import '../styles/notifications.css'


type CreateMode =
  | 'GENERAL'
  | 'DEUDA'


interface CreateNotificationModalProps {
  onClose: () => void
  onCreated: () => Promise<void>
}


function formatDateTime(
  value: string,
) {
  const date =
    new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value
  }

  return (
    new Intl.DateTimeFormat(
      'es-GT',
      {
        dateStyle: 'medium',
        timeStyle: 'short',
      },
    )
    .format(date)
  )
}


function CreateNotificationModal({
  onClose,
  onCreated,
}: CreateNotificationModalProps) {
  const [
    mode,
    setMode,
  ] =
    useState<CreateMode>(
      'GENERAL',
    )

  const [
    title,
    setTitle,
  ] =
    useState('')

  const [
    message,
    setMessage,
  ] =
    useState('')

  const [
    contactSearch,
    setContactSearch,
  ] =
    useState('')

  const [
    appliedSearch,
    setAppliedSearch,
  ] =
    useState('')

  const [
    selectedIds,
    setSelectedIds,
  ] =
    useState<number[]>([])

  const [
    localError,
    setLocalError,
  ] =
    useState<string | null>(
      null,
    )

  const contactsQuery =
    useQuery({
      queryKey: [
        'notificaciones-contactos',
        appliedSearch,
      ],

      queryFn: () =>
        buscarContactosNotificacion({
          buscar:
            appliedSearch ||
            undefined,
          limit: 50,
        }),
    })

  const createMutation =
    useMutation({
      mutationFn:
        async () => {
          if (
            selectedIds.length === 0
          ) {
            throw new Error(
              'Selecciona al menos un destinatario.',
            )
          }

          if (
            mode === 'DEUDA'
          ) {
            const selected =
              contactsQuery.data
                ?.find(
                  (contact) =>
                    contact.id_contacto ===
                    selectedIds[0],
                )

            if (!selected) {
              throw new Error(
                'No fue posible identificar el destinatario seleccionado.',
              )
            }

            return createAvisoDeuda(
              selected.id_estudiante,
              {
                id_contacto:
                  selected.id_contacto,
              },
            )
          }

          const normalizedTitle =
            title.trim()

          const normalizedMessage =
            message.trim()

          if (
            !normalizedTitle ||
            !normalizedMessage
          ) {
            throw new Error(
              'Completa el título y el mensaje.',
            )
          }

          return createNotificacion({
            titulo:
              normalizedTitle,
            mensaje:
              normalizedMessage,
            ids_contacto:
              selectedIds,
          })
        },

      onSuccess:
        async () => {
          await onCreated()
          onClose()
        },
    })

  function handleSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setAppliedSearch(
      contactSearch.trim(),
    )
  }

  function toggleContact(
    contact:
      NotificacionContacto,
  ) {
    setLocalError(null)

    if (
      mode === 'DEUDA'
    ) {
      setSelectedIds([
        contact.id_contacto,
      ])

      return
    }

    setSelectedIds(
      (current) =>
        current.includes(
          contact.id_contacto,
        )
          ? current.filter(
              (id) =>
                id !==
                contact.id_contacto,
            )
          : [
              ...current,
              contact.id_contacto,
            ],
    )
  }

  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setLocalError(null)

    if (
      selectedIds.length === 0
    ) {
      setLocalError(
        (
          'Selecciona al menos ' +
          'un destinatario.'
        ),
      )

      return
    }

    if (
      mode === 'DEUDA' &&
      selectedIds.length !== 1
    ) {
      setLocalError(
        (
          'El aviso de deuda debe ' +
          'tener un solo destinatario.'
        ),
      )

      return
    }

    if (
      mode === 'GENERAL' &&
      (
        !title.trim() ||
        !message.trim()
      )
    ) {
      setLocalError(
        (
          'Completa el título ' +
          'y el mensaje.'
        ),
      )

      return
    }

    await createMutation
      .mutateAsync()
      .catch(() => undefined)
  }

  const contacts =
    contactsQuery.data ?? []

  return (
    <div className="notification-modal-backdrop">
      <div
        className="notification-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="notification-create-title"
      >
        <header className="notification-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Comunicación
            </span>

            <h2 id="notification-create-title">
              Nueva notificación
            </h2>
          </div>

          <button
            className="notification-close-button"
            type="button"
            aria-label="Cerrar"
            disabled={
              createMutation.isPending
            }
            onClick={onClose}
          >
            <X
              size={18}
              aria-hidden="true"
            />
          </button>
        </header>

        <form
          className="notification-form"
          onSubmit={handleSubmit}
        >
          <div className="notification-mode-selector">
            <button
              className={
                mode === 'GENERAL'
                  ? 'is-active'
                  : ''
              }
              type="button"
              onClick={() => {
                setMode('GENERAL')
                setSelectedIds([])
                setLocalError(null)
              }}
            >
              Aviso general
            </button>

            <button
              className={
                mode === 'DEUDA'
                  ? 'is-active'
                  : ''
              }
              type="button"
              onClick={() => {
                setMode('DEUDA')
                setSelectedIds([])
                setLocalError(null)
              }}
            >
              Aviso de deuda
            </button>
          </div>

          {mode === 'GENERAL' && (
            <div className="notification-form-grid">
              <label className="notification-form-full">
                <span>
                  Título
                </span>

                <input
                  type="text"
                  maxLength={200}
                  value={title}
                  onChange={(event) =>
                    setTitle(
                      event.target.value,
                    )
                  }
                />
              </label>

              <label className="notification-form-full">
                <span>
                  Mensaje
                </span>

                <textarea
                  rows={4}
                  value={message}
                  onChange={(event) =>
                    setMessage(
                      event.target.value,
                    )
                  }
                />
              </label>
            </div>
          )}

          {mode === 'DEUDA' && (
            <div className="notification-info-box">
              <AlertTriangle
                size={18}
                aria-hidden="true"
              />

              <div>
                <strong>
                  Aviso automático de deuda
                </strong>

                <p>
                  El backend calculará el saldo
                  pendiente y generará el mensaje
                  con los datos del estudiante.
                </p>
              </div>
            </div>
          )}

          <section className="notification-recipient-section">
            <header>
              <div>
                <strong>
                  Destinatarios
                </strong>

                <span>
                  {mode === 'GENERAL'
                    ? (
                      'Puedes seleccionar ' +
                      'varios contactos.'
                    )
                    : (
                      'Selecciona un contacto ' +
                      'del estudiante.'
                    )}
                </span>
              </div>

              <span className="notification-selection-count">
                {selectedIds.length}
                {' '}
                seleccionado
                {selectedIds.length === 1
                  ? ''
                  : 's'}
              </span>
            </header>

            <form
              className="notification-contact-search"
              onSubmit={handleSearch}
            >
              <Search
                size={17}
                aria-hidden="true"
              />

              <input
                type="search"
                value={contactSearch}
                placeholder={
                  (
                    'Carnet, estudiante, ' +
                    'contacto, teléfono...'
                  )
                }
                onChange={(event) =>
                  setContactSearch(
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

            {contactsQuery.isLoading ? (
              <div className="module-message">
                Cargando contactos...
              </div>
            ) : contactsQuery.isError ? (
              <div className="module-message module-message-error">
                {getApiErrorMessage(
                  contactsQuery.error,
                  (
                    'No fue posible cargar ' +
                    'los contactos.'
                  ),
                )}
              </div>
            ) : contacts.length === 0 ? (
              <div className="notification-empty">
                No se encontraron contactos activos.
              </div>
            ) : (
              <div className="notification-contact-list">
                {contacts.map(
                  (contact) => {
                    const selected =
                      selectedIds.includes(
                        contact.id_contacto,
                      )

                    return (
                      <button
                        className={
                          (
                            'notification-contact-item ' +
                            (
                              selected
                                ? 'is-selected'
                                : ''
                            )
                          )
                        }
                        type="button"
                        key={
                          contact.id_contacto
                        }
                        onClick={() =>
                          toggleContact(
                            contact,
                          )
                        }
                      >
                        <span className="notification-contact-check">
                          {selected && (
                            <CheckCircle2
                              size={16}
                              aria-hidden="true"
                            />
                          )}
                        </span>

                        <span className="notification-contact-main">
                          <strong>
                            {contact.estudiante}
                          </strong>

                          <small>
                            {
                              contact
                                .codigo_estudiante
                            }
                          </small>
                        </span>

                        <span className="notification-contact-person">
                          <strong>
                            {contact.contacto}
                          </strong>

                          <small>
                            {contact.parentesco ||
                              'Sin parentesco'}
                            {contact.es_principal
                              ? ' · Principal'
                              : ''}
                          </small>
                        </span>

                        <span className="notification-contact-channel">
                          {contact.whatsapp ||
                            contact.telefono ||
                            contact.email ||
                            'Sin canal registrado'}
                        </span>
                      </button>
                    )
                  },
                )}
              </div>
            )}
          </section>

          {(localError ||
            createMutation.isError) && (
            <div className="form-error">
              {localError ||
                getApiErrorMessage(
                  createMutation.error,
                  (
                    'No fue posible crear ' +
                    'la notificación.'
                  ),
                )}
            </div>
          )}

          <footer className="notification-modal-actions">
            <button
              className="button button-secondary"
              type="button"
              disabled={
                createMutation.isPending
              }
              onClick={onClose}
            >
              Cancelar
            </button>

            <button
              className="button button-primary"
              type="submit"
              disabled={
                createMutation.isPending
              }
            >
              {createMutation.isPending
                ? 'Guardando...'
                : (
                  mode === 'DEUDA'
                    ? 'Generar aviso'
                    : 'Crear notificación'
                )}
            </button>
          </footer>
        </form>
      </div>
    </div>
  )
}


interface NotificationDetailModalProps {
  idNotificacion: number
  canManage: boolean
  onClose: () => void
  onChanged: () => Promise<void>
}


function NotificationDetailModal({
  idNotificacion,
  canManage,
  onClose,
  onChanged,
}: NotificationDetailModalProps) {
  const queryClient =
    useQueryClient()

  const notificationQuery =
    useQuery({
      queryKey: [
        'notificacion-detalle',
        idNotificacion,
      ],

      queryFn: () =>
        getNotificacion(
          idNotificacion,
        ),
    })

  const openMutation =
    useMutation({
      mutationFn: (
        idDestinatario: number,
      ) =>
        marcarDestinatarioAbierto(
          idDestinatario,
        ),

      onSuccess:
        async () => {
          await queryClient
            .invalidateQueries({
              queryKey: [
                'notificacion-detalle',
                idNotificacion,
              ],
            })

          await onChanged()
        },
    })

  const notification =
    notificationQuery.data

  return (
    <div className="notification-modal-backdrop">
      <div
        className="notification-modal notification-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="notification-detail-title"
      >
        <header className="notification-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Detalle
            </span>

            <h2 id="notification-detail-title">
              Notificación
            </h2>
          </div>

          <button
            className="notification-close-button"
            type="button"
            aria-label="Cerrar"
            onClick={onClose}
          >
            <X
              size={18}
              aria-hidden="true"
            />
          </button>
        </header>

        {notificationQuery.isLoading ? (
          <div className="module-message">
            Cargando notificación...
          </div>
        ) : notificationQuery.isError ||
          !notification ? (
          <div className="module-message module-message-error">
            {getApiErrorMessage(
              notificationQuery.error,
              (
                'No fue posible cargar ' +
                'la notificación.'
              ),
            )}
          </div>
        ) : (
          <div className="notification-detail-content">
            <section className="notification-message-card">
              <div className="notification-detail-meta">
                <span>
                  {formatDateTime(
                    notification.fecha_creacion,
                  )}
                </span>

                <span>
                  {
                    notification
                      .total_destinatarios
                  }
                  {' '}
                  destinatario
                  {
                    notification
                      .total_destinatarios === 1
                      ? ''
                      : 's'
                  }
                </span>
              </div>

              <h3>
                {notification.titulo}
              </h3>

              <p>
                {notification.mensaje}
              </p>
            </section>

            <section className="notification-detail-summary">
              <div>
                <Users
                  size={18}
                  aria-hidden="true"
                />

                <span>
                  Total
                </span>

                <strong>
                  {
                    notification
                      .total_destinatarios
                  }
                </strong>
              </div>

              <div>
                <Clock
                  size={18}
                  aria-hidden="true"
                />

                <span>
                  Generados
                </span>

                <strong>
                  {
                    notification
                      .total_pendientes
                  }
                </strong>
              </div>

              <div>
                <CheckCircle2
                  size={18}
                  aria-hidden="true"
                />

                <span>
                  Abiertos
                </span>

                <strong>
                  {
                    notification
                      .total_abiertos
                  }
                </strong>
              </div>
            </section>

            <section className="notification-destination-table-wrapper">
              <table className="notification-table">
                <thead>
                  <tr>
                    <th>
                      Estudiante
                    </th>

                    <th>
                      Contacto
                    </th>

                    <th>
                      Canales
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
                  {notification
                    .destinatarios
                    .map(
                      (recipient) => (
                        <tr
                          key={
                            recipient
                              .id_destinatario
                          }
                        >
                          <td>
                            <strong>
                              {
                                recipient
                                  .estudiante
                              }
                            </strong>

                            <small>
                              {
                                recipient
                                  .codigo_estudiante
                              }
                            </small>
                          </td>

                          <td>
                            <strong>
                              {
                                recipient
                                  .contacto
                              }
                            </strong>

                            {recipient
                              .es_principal && (
                              <small>
                                Contacto principal
                              </small>
                            )}
                          </td>

                          <td>
                            <span>
                              {
                                recipient
                                  .whatsapp ||
                                recipient
                                  .telefono ||
                                recipient
                                  .email ||
                                '—'
                              }
                            </span>
                          </td>

                          <td>
                            <span
                              className={
                                (
                                  'notification-status ' +
                                  (
                                    recipient
                                      .estado ===
                                      'ABIERTO'
                                      ? 'notification-status-open'
                                      : 'notification-status-generated'
                                  )
                                )
                              }
                            >
                              {
                                recipient
                                  .estado ===
                                  'ABIERTO'
                                  ? 'Abierto'
                                  : 'Generado'
                              }
                            </span>
                          </td>

                          <td>
                            {canManage &&
                            recipient.estado ===
                              'GENERADO' ? (
                              <button
                                className="button button-secondary notification-small-button"
                                type="button"
                                disabled={
                                  openMutation
                                    .isPending
                                }
                                onClick={() =>
                                  openMutation
                                    .mutate(
                                      recipient
                                        .id_destinatario,
                                    )
                                }
                              >
                                Marcar abierto
                              </button>
                            ) : (
                              '—'
                            )}
                          </td>
                        </tr>
                      ),
                    )}
                </tbody>
              </table>
            </section>

            {openMutation.isError && (
              <div className="form-error">
                {getApiErrorMessage(
                  openMutation.error,
                  (
                    'No fue posible actualizar ' +
                    'el destinatario.'
                  ),
                )}
              </div>
            )}
          </div>
        )}

        <footer className="notification-modal-actions">
          <button
            className="button button-secondary"
            type="button"
            onClick={onClose}
          >
            Cerrar
          </button>
        </footer>
      </div>
    </div>
  )
}


function NotificationsPage() {
  const {
    hasAnyPermission,
  } = useAuth()

  const queryClient =
    useQueryClient()

  const canManage =
    hasAnyPermission([
      PERMISSIONS
        .NOTIFICACIONES_GESTIONAR,
    ])

  const [
    searchDraft,
    setSearchDraft,
  ] =
    useState('')

  const [
    search,
    setSearch,
  ] =
    useState('')

  const [
    statusFilter,
    setStatusFilter,
  ] =
    useState<
      EstadoDestinatario |
      ''
    >('')

  const [
    showCreate,
    setShowCreate,
  ] =
    useState(false)

  const [
    selectedNotificationId,
    setSelectedNotificationId,
  ] =
    useState<number | null>(
      null,
    )

  const notificationsQuery =
    useQuery({
      queryKey: [
        'notificaciones',
        statusFilter,
      ],

      queryFn: () =>
        getNotificaciones({
          estado_destinatario:
            statusFilter ||
            undefined,
          offset: 0,
          limit: 100,
        }),
    })

  const notifications =
    notificationsQuery.data ?? []

  const filteredNotifications =
    useMemo(
      () => {
        const term =
          search.trim()
            .toLocaleLowerCase(
              'es',
            )

        if (!term) {
          return notifications
        }

        return notifications
          .filter(
            (notification) =>
              (
                notification.titulo
                  .toLocaleLowerCase(
                    'es',
                  )
                  .includes(term) ||
                notification.mensaje
                  .toLocaleLowerCase(
                    'es',
                  )
                  .includes(term)
              ),
          )
      },
      [
        notifications,
        search,
      ],
    )

  const totals =
    useMemo(
      () => ({
        notifications:
          notifications.length,

        recipients:
          notifications.reduce(
            (
              total,
              notification,
            ) =>
              total +
              notification
                .total_destinatarios,
            0,
          ),

        pending:
          notifications.reduce(
            (
              total,
              notification,
            ) =>
              total +
              notification
                .total_pendientes,
            0,
          ),
      }),
      [
        notifications,
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

  async function refreshNotifications() {
    await queryClient
      .invalidateQueries({
        queryKey: [
          'notificaciones',
        ],
      })
  }

  return (
    <main className="module-page notification-page">
      <header className="module-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Comunicación
          </span>

          <h1>
            Notificaciones
          </h1>

          <p>
            Avisos generales, avisos de deuda
            y seguimiento de destinatarios.
          </p>
        </div>

        {canManage && (
          <button
            className="button button-primary"
            type="button"
            onClick={() =>
              setShowCreate(true)
            }
          >
            <Plus
              size={17}
              aria-hidden="true"
            />

            Nueva notificación
          </button>
        )}
      </header>

      <section className="notification-summary-grid">
        <article className="module-card notification-summary-card">
          <Bell
            size={20}
            aria-hidden="true"
          />

          <div>
            <span>
              Notificaciones
            </span>

            <strong>
              {totals.notifications}
            </strong>
          </div>
        </article>

        <article className="module-card notification-summary-card">
          <Users
            size={20}
            aria-hidden="true"
          />

          <div>
            <span>
              Destinatarios
            </span>

            <strong>
              {totals.recipients}
            </strong>
          </div>
        </article>

        <article className="module-card notification-summary-card">
          <Clock
            size={20}
            aria-hidden="true"
          />

          <div>
            <span>
              Generados pendientes
            </span>

            <strong>
              {totals.pending}
            </strong>
          </div>
        </article>
      </section>

      <section className="module-card">
        <div className="notification-toolbar">
          <form
            className="notification-search"
            onSubmit={handleSearch}
          >
            <Search
              size={18}
              aria-hidden="true"
            />

            <input
              type="search"
              value={searchDraft}
              placeholder={
                'Buscar por título o mensaje...'
              }
              onChange={(event) =>
                setSearchDraft(
                  event.target.value,
                )
              }
            />

            <button type="submit">
              Buscar
            </button>
          </form>

          <label className="notification-filter">
            <span>
              Estado del destinatario
            </span>

            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value as
                    EstadoDestinatario |
                    '',
                )
              }
            >
              <option value="">
                Todos
              </option>

              <option value="GENERADO">
                Generado
              </option>

              <option value="ABIERTO">
                Abierto
              </option>
            </select>
          </label>
        </div>

        {notificationsQuery.isLoading ? (
          <div className="module-message">
            Cargando notificaciones...
          </div>
        ) : notificationsQuery.isError ? (
          <div className="module-message module-message-error">
            <p>
              {getApiErrorMessage(
                notificationsQuery.error,
                (
                  'No fue posible cargar ' +
                  'las notificaciones.'
                ),
              )}
            </p>

            <button
              className="button button-secondary"
              type="button"
              onClick={() => {
                void notificationsQuery
                  .refetch()
              }}
            >
              Reintentar
            </button>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="notification-empty notification-empty-main">
            <Bell
              size={34}
              aria-hidden="true"
            />

            <strong>
              No hay notificaciones
            </strong>

            <p>
              Ajusta los filtros o crea
              una nueva notificación.
            </p>
          </div>
        ) : (
          <div className="notification-list">
            {filteredNotifications
              .map(
                (notification) => (
                  <article
                    className="notification-list-card"
                    key={
                      notification
                        .id_notificacion
                    }
                  >
                    <div className="notification-list-icon">
                      <Bell
                        size={19}
                        aria-hidden="true"
                      />
                    </div>

                    <div className="notification-list-content">
                      <div className="notification-list-heading">
                        <div>
                          <strong>
                            {
                              notification
                                .titulo
                            }
                          </strong>

                          <span>
                            {formatDateTime(
                              notification
                                .fecha_creacion,
                            )}
                          </span>
                        </div>

                        <button
                          className="table-icon-button"
                          type="button"
                          title="Ver detalle"
                          aria-label="Ver detalle"
                          onClick={() =>
                            setSelectedNotificationId(
                              notification
                                .id_notificacion,
                            )
                          }
                        >
                          <Eye
                            size={17}
                            aria-hidden="true"
                          />
                        </button>
                      </div>

                      <p>
                        {notification.mensaje}
                      </p>

                      <footer className="notification-list-footer">
                        <span>
                          <Users
                            size={14}
                            aria-hidden="true"
                          />

                          {
                            notification
                              .total_destinatarios
                          }
                          {' '}
                          destinatarios
                        </span>

                        <span>
                          <Clock
                            size={14}
                            aria-hidden="true"
                          />

                          {
                            notification
                              .total_pendientes
                          }
                          {' '}
                          generados
                        </span>

                        <span>
                          <CheckCircle2
                            size={14}
                            aria-hidden="true"
                          />

                          {
                            notification
                              .total_abiertos
                          }
                          {' '}
                          abiertos
                        </span>
                      </footer>
                    </div>
                  </article>
                ),
              )}
          </div>
        )}
      </section>

      {showCreate && (
        <CreateNotificationModal
          onClose={() =>
            setShowCreate(false)
          }
          onCreated={
            refreshNotifications
          }
        />
      )}

      {selectedNotificationId !==
        null && (
        <NotificationDetailModal
          idNotificacion={
            selectedNotificationId
          }
          canManage={canManage}
          onClose={() =>
            setSelectedNotificationId(
              null,
            )
          }
          onChanged={
            refreshNotifications
          }
        />
      )}
    </main>
  )
}


export default NotificationsPage
