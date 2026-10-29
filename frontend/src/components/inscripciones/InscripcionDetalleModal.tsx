import {
  Printer,
  X,
} from 'lucide-react'

import {
  useQuery,
} from '@tanstack/react-query'

import {
  getContactos,
} from '../../api/contactos'

import {
  getEstudiante,
} from '../../api/estudiantes'

import {
  PERMISSIONS,
} from '../../auth/permissions'

import {
  useAuth,
} from '../../auth/useAuth'

import type {
  InscripcionDetalle,
} from '../../types/inscripcion'

import {
  printInscripcionComprobante,
} from '../../utils/printInscripcion'


interface Props {
  inscripcion:
    InscripcionDetalle

  onClose: () => void
}


function display(
  value:
    string |
    null |
    undefined,
) {
  return value?.trim()
    ? value
    : 'No registrado'
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


function InscripcionDetalleModal({
  inscripcion,
  onClose,
}: Props) {
  const {
    hasAnyPermission,
  } = useAuth()

  const canViewContacts =
    hasAnyPermission([
      PERMISSIONS
        .EXPEDIENTES_VER,
    ])

  const studentQuery =
    useQuery({
      queryKey: [
        'estudiante',
        inscripcion.id_estudiante,
      ],

      queryFn: () =>
        getEstudiante(
          inscripcion.id_estudiante,
        ),
    })

  const contactsQuery =
    useQuery({
      queryKey: [
        'contactos-estudiante',
        inscripcion.id_estudiante,
      ],

      queryFn: () =>
        getContactos(
          inscripcion.id_estudiante,
          true,
        ),

      enabled:
        canViewContacts,
    })

  const estudiante =
    studentQuery.data ??
    null

  const contactos =
    contactsQuery.data ??
    []

  const principal =
    contactos.find(
      (contacto) =>
        contacto.es_principal,
    ) ?? null

  const preparing =
    studentQuery.isLoading ||
    (
      canViewContacts &&
      contactsQuery.isLoading
    )

  function handlePrint() {
    printInscripcionComprobante({
      inscripcion,
      estudiante,
      contactoPrincipal:
        principal,
    })
  }

  return (
    <div
      className="modal-backdrop"
      role="presentation"
    >
      <section
        className="student-modal enrollment-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="inscripcion-detail-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Inscripciones
            </span>

            <h2 id="inscripcion-detail-title">
              Detalle de inscripción
            </h2>
          </div>

          <button
            className="modal-close"
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
          >
            <X
              size={19}
              aria-hidden="true"
            />
          </button>
        </header>

        <div className="enrollment-detail-body">
          <div className="enrollment-detail-highlight">
            <div>
              <span>
                Código / Carnet
              </span>

              <strong>
                {
                  inscripcion
                    .codigo_estudiante
                }
              </strong>
            </div>

            <div>
              <span>
                Estudiante
              </span>

              <strong>
                {inscripcion.estudiante}
              </strong>
            </div>

            <div>
              <span>
                No. inscripción
              </span>

              <strong>
                INS-
                {String(
                  inscripcion
                    .id_inscripcion,
                ).padStart(
                  6,
                  '0',
                )}
              </strong>
            </div>
          </div>

          <div className="enrollment-detail-grid">
            <article>
              <span>
                Fecha
              </span>

              <strong>
                {formatDate(
                  inscripcion
                    .fecha_inscripcion,
                )}
              </strong>
            </article>

            <article>
              <span>
                Estado
              </span>

              <strong>
                {inscripcion.estado}
              </strong>
            </article>

            <article>
              <span>
                Ciclo
              </span>

              <strong>
                {inscripcion.ciclo}
              </strong>
            </article>

            <article>
              <span>
                Carrera
              </span>

              <strong>
                {inscripcion.carrera}
              </strong>
            </article>

            <article>
              <span>
                Grado
              </span>

              <strong>
                {inscripcion.grado}
              </strong>
            </article>

            <article>
              <span>
                Tipo
              </span>

              <strong>
                {inscripcion.tipo}
              </strong>
            </article>

            <article>
              <span>
                CUI
              </span>

              <strong>
                {display(
                  estudiante?.cui,
                )}
              </strong>
            </article>

            <article>
              <span>
                Teléfono estudiante
              </span>

              <strong>
                {display(
                  estudiante?.telefono,
                )}
              </strong>
            </article>

            <article>
              <span>
                Encargado principal
              </span>

              <strong>
                {display(
                  principal?.nombre,
                )}
              </strong>
            </article>

            <article>
              <span>
                Parentesco
              </span>

              <strong>
                {display(
                  principal?.parentesco,
                )}
              </strong>
            </article>

            <article>
              <span>
                Teléfono encargado
              </span>

              <strong>
                {display(
                  principal?.telefono,
                )}
              </strong>
            </article>

            <article>
              <span>
                WhatsApp encargado
              </span>

              <strong>
                {display(
                  principal?.whatsapp,
                )}
              </strong>
            </article>
          </div>

          {inscripcion.observaciones && (
            <div className="enrollment-detail-observations">
              <span>
                Observaciones
              </span>

              <p>
                {
                  inscripcion
                    .observaciones
                }
              </p>
            </div>
          )}

          {studentQuery.isError && (
            <div className="form-error">
              No fue posible cargar
              todos los datos personales
              del estudiante.
            </div>
          )}
        </div>

        <footer className="student-modal-actions">
          <button
            className="button button-secondary"
            type="button"
            onClick={onClose}
          >
            Cerrar
          </button>

          <button
            className="button button-primary"
            type="button"
            disabled={preparing}
            onClick={
              handlePrint
            }
          >
            <Printer
              size={16}
              aria-hidden="true"
            />

            {preparing
              ? 'Preparando...'
              : 'Imprimir comprobante'}
          </button>
        </footer>
      </section>
    </div>
  )
}


export default InscripcionDetalleModal