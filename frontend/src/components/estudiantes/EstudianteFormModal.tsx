import {
  useState,
  type FormEvent,
} from 'react'

import {
  X,
} from 'lucide-react'

import type {
  Estudiante,
  EstudianteCreate,
} from '../../types/estudiante'


interface Props {
  title: string

  estudiante?: Estudiante

  isSubmitting: boolean
  error: string | null

  onClose: () => void

  onSubmit: (
    payload: EstudianteCreate,
  ) => Promise<void>
}


interface FormState {
  cui: string
  nombres: string
  apellidos: string

  fecha_nacimiento: string

  telefono: string
  whatsapp: string
  email: string

  direccion: string
}


function initialState(
  estudiante?: Estudiante,
): FormState {
  return {
    cui:
      estudiante?.cui ?? '',

    nombres:
      estudiante?.nombres ?? '',

    apellidos:
      estudiante?.apellidos ?? '',

    fecha_nacimiento:
      estudiante
        ?.fecha_nacimiento ?? '',

    telefono:
      estudiante?.telefono ?? '',

    whatsapp:
      estudiante?.whatsapp ?? '',

    email:
      estudiante?.email ?? '',

    direccion:
      estudiante?.direccion ?? '',
  }
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


function EstudianteFormModal({
  title,
  estudiante,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [
    form,
    setForm,
  ] = useState<FormState>(
    () =>
      initialState(
        estudiante,
      ),
  )

  function updateField(
    field: keyof FormState,
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

    const payload:
      EstudianteCreate = {
        nombres:
          form.nombres.trim(),

        apellidos:
          form.apellidos.trim(),

        cui:
          nullable(
            form.cui,
          ),

        fecha_nacimiento:
          nullable(
            form.fecha_nacimiento,
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

        direccion:
          nullable(
            form.direccion,
          ),
      }

    await onSubmit(
      payload,
    )
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
        aria-labelledby="student-modal-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Estudiantes
            </span>

            <h2 id="student-modal-title">
              {title}
            </h2>
          </div>

          <button
            type="button"
            className="modal-close"
            onClick={onClose}
            disabled={
              isSubmitting
            }
            aria-label="Cerrar"
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
            <div className="form-field">
              <label htmlFor="codigo">
                Código / Carnet
              </label>

              <input
                id="codigo"
                value={
                  estudiante
                    ?.codigo_estudiante ??
                  (
                    'Se asignará ' +
                    'automáticamente'
                  )
                }
                readOnly
              />
            </div>

            <div className="form-field">
              <label htmlFor="cui">
                CUI
              </label>

              <input
                id="cui"
                value={
                  form.cui
                }
                maxLength={30}
                onChange={(event) =>
                  updateField(
                    'cui',
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="nombres">
                Nombres *
              </label>

              <input
                id="nombres"
                value={
                  form.nombres
                }
                maxLength={150}
                required
                onChange={(event) =>
                  updateField(
                    'nombres',
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="apellidos">
                Apellidos *
              </label>

              <input
                id="apellidos"
                value={
                  form.apellidos
                }
                maxLength={150}
                required
                onChange={(event) =>
                  updateField(
                    'apellidos',
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="fechaNacimiento">
                Fecha de nacimiento
              </label>

              <input
                id="fechaNacimiento"
                type="date"
                value={
                  form.fecha_nacimiento
                }
                onChange={(event) =>
                  updateField(
                    'fecha_nacimiento',
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="telefono">
                Teléfono
              </label>

              <input
                id="telefono"
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
              <label htmlFor="whatsapp">
                WhatsApp
              </label>

              <input
                id="whatsapp"
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
              <label htmlFor="email">
                Correo electrónico
              </label>

              <input
                id="email"
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

            <div className="form-field student-form-full">
              <label htmlFor="direccion">
                Dirección
              </label>

              <textarea
                id="direccion"
                rows={3}
                value={
                  form.direccion
                }
                onChange={(event) =>
                  updateField(
                    'direccion',
                    event.target.value,
                  )
                }
              />
            </div>
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
              onClick={onClose}
              disabled={
                isSubmitting
              }
            >
              Cancelar
            </button>

            <button
              className="button button-primary"
              type="submit"
              disabled={
                isSubmitting
              }
            >
              {isSubmitting
                ? 'Guardando...'
                : 'Guardar'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default EstudianteFormModal