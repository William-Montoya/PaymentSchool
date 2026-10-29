import {
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import type {
  Contacto,
  ContactoCreate,
} from '../../types/contacto'


interface ContactoFormModalProps {
  idEstudiante: number

  contacto?: Contacto

  isSubmitting: boolean
  error: string | null

  onClose: () => void

  onSubmit: (
    payload: ContactoCreate,
  ) => Promise<void>
}


interface FormState {
  nombre: string
  parentesco: string

  telefono: string
  whatsapp: string
  email: string

  es_principal: boolean
}


function nullable(
  value: string,
): string | null {
  const normalized =
    value.trim()

  return normalized
    ? normalized
    : null
}


function initialState(
  contacto?: Contacto,
): FormState {
  return {
    nombre:
      contacto?.nombre ?? '',

    parentesco:
      contacto?.parentesco ?? '',

    telefono:
      contacto?.telefono ?? '',

    whatsapp:
      contacto?.whatsapp ?? '',

    email:
      contacto?.email ?? '',

    es_principal:
      contacto?.es_principal ??
      false,
  }
}


function ContactoFormModal({
  idEstudiante,
  contacto,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: ContactoFormModalProps) {
  const [
    form,
    setForm,
  ] = useState<FormState>(
    () =>
      initialState(
        contacto,
      ),
  )

  function updateField(
    field:
      keyof Omit<
        FormState,
        'es_principal'
      >,
    value: string,
  ) {
    setForm(
      (current) => ({
        ...current,
        [field]:
          value,
      }),
    )
  }

  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    await onSubmit({
      id_estudiante:
        idEstudiante,

      nombre:
        form.nombre.trim(),

      parentesco:
        nullable(
          form.parentesco,
        ),

      telefono:
        nullable(
          form.telefono,
        ),

      whatsapp:
        nullable(
          form.whatsapp,
        ),

      email:
        nullable(
          form.email,
        ),

      es_principal:
        form.es_principal,
    })
  }

  return (
    <div
      className="modal-backdrop"
      role="presentation"
    >
      <section
        className="student-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="contacto-modal-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Encargados
            </span>

            <h2 id="contacto-modal-title">
              {contacto
                ? 'Editar encargado'
                : 'Agregar encargado'}
            </h2>
          </div>

          <button
            className="modal-close"
            type="button"
            aria-label="Cerrar"
            disabled={
              isSubmitting
            }
            onClick={onClose}
          >
            <X
              size={19}
              aria-hidden="true"
            />
          </button>
        </header>

        <form
          className="student-form"
          onSubmit={handleSubmit}
        >
          <div className="student-form-grid">
            <div className="form-field student-form-full">
              <label htmlFor="contacto-nombre">
                Nombre completo *
              </label>

              <input
                id="contacto-nombre"
                value={
                  form.nombre
                }
                maxLength={150}
                required
                autoFocus
                onChange={(event) =>
                  updateField(
                    'nombre',
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="contacto-parentesco">
                Parentesco
              </label>

              <input
                id="contacto-parentesco"
                value={
                  form.parentesco
                }
                maxLength={100}
                list="parentescos-sugeridos"
                placeholder="Ej. Madre"
                onChange={(event) =>
                  updateField(
                    'parentesco',
                    event.target.value,
                  )
                }
              />

              <datalist id="parentescos-sugeridos">
                <option value="Madre" />
                <option value="Padre" />
                <option value="Tutor" />
                <option value="Abuelo" />
                <option value="Abuela" />
                <option value="Tío" />
                <option value="Tía" />
                <option value="Hermano" />
                <option value="Hermana" />
                <option value="Encargado" />
              </datalist>
            </div>

            <div className="form-field">
              <label htmlFor="contacto-telefono">
                Teléfono
              </label>

              <input
                id="contacto-telefono"
                value={
                  form.telefono
                }
                maxLength={30}
                onChange={(event) =>
                  updateField(
                    'telefono',
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="contacto-whatsapp">
                WhatsApp
              </label>

              <input
                id="contacto-whatsapp"
                value={
                  form.whatsapp
                }
                maxLength={30}
                onChange={(event) =>
                  updateField(
                    'whatsapp',
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="contacto-email">
                Correo electrónico
              </label>

              <input
                id="contacto-email"
                type="email"
                value={
                  form.email
                }
                onChange={(event) =>
                  updateField(
                    'email',
                    event.target.value,
                  )
                }
              />
            </div>

            <label className="contact-primary-check student-form-full">
              <input
                type="checkbox"
                checked={
                  form.es_principal
                }
                onChange={(event) =>
                  setForm(
                    (current) => ({
                      ...current,
                      es_principal:
                        event.target
                          .checked,
                    }),
                  )
                }
              />

              <span>
                <strong>
                  Contacto principal
                </strong>

                <small>
                  Se utilizará como
                  contacto preferido del
                  estudiante.
                </small>
              </span>
            </label>
          </div>

          {error && (
            <div
              className="form-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <footer className="student-modal-actions">
            <button
              className="button button-secondary"
              type="button"
              disabled={
                isSubmitting
              }
              onClick={onClose}
            >
              Cancelar
            </button>

            <button
              className="button button-primary"
              type="submit"
              disabled={
                isSubmitting ||
                !form.nombre.trim()
              }
            >
              {isSubmitting
                ? 'Guardando...'
                : contacto
                  ? 'Guardar cambios'
                  : 'Agregar encargado'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default ContactoFormModal