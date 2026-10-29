import {
  Mail,
  MessageCircle,
  Pencil,
  Phone,
  Plus,
  Star,
  UserRound,
} from 'lucide-react'

import {
  useEffect,
  useState,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  createContacto,
  getContactos,
  updateContacto,
} from '../../api/contactos'

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
  Contacto,
  ContactoCreate,
  ContactoUpdate,
} from '../../types/contacto'

import ContactoFormModal from
  './ContactoFormModal'


interface ContactosStepProps {
  idEstudiante: number

  onContactsChange?: (
    contactos: Contacto[],
  ) => void
}


interface UpdatePayload {
  idContacto: number
  payload: ContactoUpdate
}


function ContactosStep({
  idEstudiante,
  onContactsChange,
}: ContactosStepProps) {
  const queryClient =
    useQueryClient()

  const {
    hasAnyPermission,
  } = useAuth()

  const canView =
    hasAnyPermission([
      PERMISSIONS
        .EXPEDIENTES_VER,
    ])

  const canManage =
    hasAnyPermission([
      PERMISSIONS
        .EXPEDIENTES_GESTIONAR,
    ])

  const [
    showForm,
    setShowForm,
  ] = useState(false)

  const [
    editingContacto,
    setEditingContacto,
  ] = useState<
    Contacto |
    undefined
  >(undefined)

  const contactsQuery =
    useQuery({
      queryKey: [
        'contactos-estudiante',
        idEstudiante,
      ],

      queryFn: () =>
        getContactos(
          idEstudiante,
          true,
        ),

      enabled:
        canView,
    })

  const createMutation =
    useMutation({
      mutationFn:
        createContacto,

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'contactos-estudiante',
              idEstudiante,
            ],
          })

        setShowForm(false)

        setEditingContacto(
          undefined,
        )
      },
    })

  const updateMutation =
    useMutation({
      mutationFn: (
        data:
          UpdatePayload,
      ) =>
        updateContacto(
          data.idContacto,
          data.payload,
        ),

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'contactos-estudiante',
              idEstudiante,
            ],
          })

        setShowForm(false)

        setEditingContacto(
          undefined,
        )
      },
    })

  const contactos =
    contactsQuery.data ?? []

  useEffect(
    () => {
      onContactsChange?.(
        contactos,
      )
    },
    [
      contactos,
      onContactsChange,
    ],
  )

  function openCreate() {
    createMutation.reset()
    updateMutation.reset()

    setEditingContacto(
      undefined,
    )

    setShowForm(true)
  }

  function openEdit(
    contacto: Contacto,
  ) {
    createMutation.reset()
    updateMutation.reset()

    setEditingContacto(
      contacto,
    )

    setShowForm(true)
  }

  function closeForm() {
    if (
      createMutation.isPending ||
      updateMutation.isPending
    ) {
      return
    }

    createMutation.reset()
    updateMutation.reset()

    setShowForm(false)

    setEditingContacto(
      undefined,
    )
  }

  async function handleSubmit(
    payload: ContactoCreate,
  ) {
    if (!editingContacto) {
      await createMutation
        .mutateAsync(
          payload,
        )

      return
    }

    await updateMutation
      .mutateAsync({
        idContacto:
          editingContacto
            .id_contacto,

        payload: {
          nombre:
            payload.nombre,

          parentesco:
            payload.parentesco ??
            null,

          telefono:
            payload.telefono ??
            null,

          whatsapp:
            payload.whatsapp ??
            null,

          email:
            payload.email ??
            null,

          es_principal:
            payload.es_principal ??
            false,
        },
      })
  }

  if (!canView) {
    return (
      <div className="enrollment-info-box">
        <UserRound
          size={20}
          aria-hidden="true"
        />

        <div>
          <strong>
            Contactos no disponibles
          </strong>

          <p>
            Tu usuario no posee permiso
            para consultar los encargados
            del estudiante. Puedes
            continuar con la inscripción.
          </p>
        </div>
      </div>
    )
  }

  if (contactsQuery.isLoading) {
    return (
      <div className="module-message">
        Cargando encargados...
      </div>
    )
  }

  if (contactsQuery.isError) {
    return (
      <div className="module-message module-message-error">
        <p>
          {getApiErrorMessage(
            contactsQuery.error,
            (
              'No fue posible cargar ' +
              'los encargados.'
            ),
          )}
        </p>

        <button
          className="button button-secondary"
          type="button"
          onClick={() => {
            void contactsQuery
              .refetch()
          }}
        >
          Reintentar
        </button>
      </div>
    )
  }

  const principal =
    contactos.find(
      (contacto) =>
        contacto.es_principal,
    ) ?? null

  return (
    <>
      <div className="contact-step">
        <div className="contact-step-toolbar">
          <div>
            <strong>
              Encargados registrados
            </strong>

            <small>
              {contactos.length}
              {' '}
              {contactos.length === 1
                ? 'contacto activo'
                : 'contactos activos'}
            </small>
          </div>

          {canManage && (
            <button
              className="button button-primary"
              type="button"
              onClick={
                openCreate
              }
            >
              <Plus
                size={16}
                aria-hidden="true"
              />

              Agregar encargado
            </button>
          )}
        </div>

        {contactos.length === 0 ? (
          <div className="enrollment-empty-card contact-empty-card">
            <UserRound
              size={36}
              aria-hidden="true"
            />

            <strong>
              No hay encargados registrados
            </strong>

            <p>
              Puedes agregar madre, padre,
              tutor u otro contacto del
              estudiante.
            </p>

            {canManage && (
              <button
                className="button button-primary"
                type="button"
                onClick={
                  openCreate
                }
              >
                <Plus
                  size={16}
                  aria-hidden="true"
                />

                Agregar primer encargado
              </button>
            )}
          </div>
        ) : (
          <div className="contact-card-grid">
            {contactos.map(
              (contacto) => (
                <article
                  className={
                    (
                      'contact-card ' +
                      (
                        contacto
                          .es_principal
                          ? 'contact-card-primary'
                          : ''
                      )
                    )
                  }
                  key={
                    contacto.id_contacto
                  }
                >
                  <header className="contact-card-header">
                    <div className="contact-card-title">
                      <div className="contact-avatar">
                        {contacto.nombre
                          .charAt(0)
                          .toUpperCase()}
                      </div>

                      <div>
                        <strong>
                          {contacto.nombre}
                        </strong>

                        <span>
                          {contacto.parentesco ||
                            'Sin parentesco'}
                        </span>
                      </div>
                    </div>

                    {contacto
                      .es_principal && (
                      <span className="contact-primary-badge">
                        <Star
                          size={12}
                          aria-hidden="true"
                        />

                        Principal
                      </span>
                    )}
                  </header>

                  <div className="contact-card-details">
                    <div>
                      <Phone
                        size={14}
                        aria-hidden="true"
                      />

                      <span>
                        {contacto.telefono ||
                          'Sin teléfono'}
                      </span>
                    </div>

                    <div>
                      <MessageCircle
                        size={14}
                        aria-hidden="true"
                      />

                      <span>
                        {contacto.whatsapp ||
                          'Sin WhatsApp'}
                      </span>
                    </div>

                    <div>
                      <Mail
                        size={14}
                        aria-hidden="true"
                      />

                      <span>
                        {contacto.email ||
                          'Sin correo'}
                      </span>
                    </div>
                  </div>

                  {canManage && (
                    <footer className="contact-card-actions">
                      <button
                        className="button button-secondary"
                        type="button"
                        onClick={() =>
                          openEdit(
                            contacto,
                          )
                        }
                      >
                        <Pencil
                          size={14}
                          aria-hidden="true"
                        />

                        Editar
                      </button>
                    </footer>
                  )}
                </article>
              ),
            )}
          </div>
        )}

        {contactos.length > 0 &&
          !principal && (
            <div className="enrollment-warning-box">
              Ningún encargado está
              definido como contacto
              principal. Puedes continuar,
              pero conviene seleccionar uno.
            </div>
          )}
      </div>

      {showForm && (
        <ContactoFormModal
          idEstudiante={
            idEstudiante
          }
          contacto={
            editingContacto
          }
          isSubmitting={
            createMutation.isPending ||
            updateMutation.isPending
          }
          error={
            createMutation.isError
              ? getApiErrorMessage(
                  createMutation.error,
                  (
                    'No fue posible crear ' +
                    'el encargado.'
                  ),
                )
              : updateMutation.isError
                ? getApiErrorMessage(
                    updateMutation.error,
                    (
                      'No fue posible ' +
                      'actualizar el encargado.'
                    ),
                  )
                : null
          }
          onClose={
            closeForm
          }
          onSubmit={
            handleSubmit
          }
        />
      )}
    </>
  )
}


export default ContactosStep