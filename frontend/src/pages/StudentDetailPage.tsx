import {
  ArrowLeft,
  CalendarDays,
  Mail,
  MapPin,
  MessageCircle,
  Pencil,
  Phone,
  RefreshCcw,
  UserRound,
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
  useNavigate,
  useParams,
} from 'react-router-dom'

import {
  getEstudiante,
  updateEstadoEstudiante,
  updateEstudiante,
} from '../api/estudiantes'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  PERMISSIONS,
} from '../auth/permissions'

import PermissionGate from
  '../auth/PermissionGate'

import EstudianteEstadoBadge from
  '../components/estudiantes/EstudianteEstadoBadge'

import EstudianteEstadoModal from
  '../components/estudiantes/EstudianteEstadoModal'

import EstudianteFormModal from
  '../components/estudiantes/EstudianteFormModal'

import type {
  EstadoEstudiante,
  EstudianteCreate,
} from '../types/estudiante'

function StudentDetailPage() {
  const navigate =
    useNavigate()

  const params =
    useParams()

  const queryClient =
    useQueryClient()

  const [
    showEdit,
    setShowEdit,
  ] =
    useState(false)

  const [
    showState,
    setShowState,
  ] =
    useState(false)

  const idEstudiante =
    Number(
      params.idEstudiante,
    )

  const studentQuery =
    useQuery({
      queryKey: [
        'estudiante',
        idEstudiante,
      ],

      queryFn: () =>
        getEstudiante(
          idEstudiante,
        ),

      enabled:
        Number.isInteger(
          idEstudiante,
        ) &&
        idEstudiante > 0,
    })

  const updateMutation =
    useMutation({
      mutationFn:
        (
          payload:
            EstudianteCreate,
        ) =>
          updateEstudiante(
            idEstudiante,
            payload,
          ),

      onSuccess: async () => {
        await Promise.all([
          queryClient.invalidateQueries({
            queryKey: [
              'estudiante',
              idEstudiante,
            ],
          }),

          queryClient.invalidateQueries({
            queryKey: [
              'estudiantes',
            ],
          }),
        ])

        setShowEdit(false)
      },
    })

  const stateMutation =
    useMutation({
      mutationFn:
        (
          estado:
            EstadoEstudiante,
        ) =>
          updateEstadoEstudiante(
            idEstudiante,
            estado,
          ),

      onSuccess: async () => {
        await Promise.all([
          queryClient.invalidateQueries({
            queryKey: [
              'estudiante',
              idEstudiante,
            ],
          }),

          queryClient.invalidateQueries({
            queryKey: [
              'estudiantes',
            ],
          }),
        ])

        setShowState(false)
      },
    })

  if (
    !Number.isInteger(
      idEstudiante,
    ) ||
    idEstudiante <= 0
  ) {
    return (
      <main className="module-page">
        <div className="module-message module-message-error">
          Identificador de estudiante
          inválido.
        </div>
      </main>
    )
  }

  if (studentQuery.isLoading) {
    return (
      <main className="module-page">
        <div className="module-message">
          Cargando estudiante...
        </div>
      </main>
    )
  }

  if (
    studentQuery.isError ||
    !studentQuery.data
  ) {
    return (
      <main className="module-page">
        <div className="module-message module-message-error">
          <p>
            {getApiErrorMessage(
              studentQuery.error,
              'No fue posible obtener el estudiante.',
            )}
          </p>

          <button
            className="button button-secondary"
            type="button"
            onClick={() =>
              navigate('/estudiantes')
            }
          >
            Volver
          </button>
        </div>
      </main>
    )
  }

  const student =
    studentQuery.data

  const formattedBirthDate =
    student.fecha_nacimiento
      ? new Intl.DateTimeFormat(
          'es-GT',
          {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
          },
        ).format(
          new Date(
            `${student.fecha_nacimiento}T00:00:00`,
          ),
        )
      : 'No registrada'

  return (
    <main className="module-page">
      <header className="module-header student-detail-header">
        <div>
          <button
            className="back-button"
            type="button"
            onClick={() =>
              navigate('/estudiantes')
            }
          >
            <ArrowLeft
              size={17}
              aria-hidden="true"
            />

            Estudiantes
          </button>

          <div className="student-detail-title">
            <div className="student-detail-avatar">
              {student.nombres
                .charAt(0)
                .toUpperCase()}

              {student.apellidos
                .charAt(0)
                .toUpperCase()}
            </div>

            <div>
              <span className="dashboard-card-eyebrow">
                {
                  student.codigo_estudiante
                }
              </span>

              <h1>
                {student.nombres}
                {' '}
                {student.apellidos}
              </h1>

              <EstudianteEstadoBadge
                estado={
                  student.estado
                }
              />
            </div>
          </div>
        </div>

        <PermissionGate
          anyOf={[
            PERMISSIONS
              .ESTUDIANTES_GESTIONAR,
          ]}
        >
          <div className="student-detail-actions">
            <button
              className="button button-secondary"
              type="button"
              onClick={() =>
                setShowState(true)
              }
            >
              <RefreshCcw
                size={16}
                aria-hidden="true"
              />

              Cambiar estado
            </button>

            <button
              className="button button-primary"
              type="button"
              onClick={() =>
                setShowEdit(true)
              }
            >
              <Pencil
                size={16}
                aria-hidden="true"
              />

              Editar
            </button>
          </div>
        </PermissionGate>
      </header>

      <section className="student-detail-grid">
        <article className="module-card">
          <header className="detail-card-header">
            <UserRound
              size={19}
              aria-hidden="true"
            />

            <div>
              <h2>
                Información personal
              </h2>

              <p>
                Datos generales del
                estudiante.
              </p>
            </div>
          </header>

          <dl className="student-detail-list">
            <div>
              <dt>
                Código
              </dt>

              <dd>
                {
                  student.codigo_estudiante
                }
              </dd>
            </div>

            <div>
              <dt>
                CUI
              </dt>

              <dd>
                {student.cui ??
                  'No registrado'}
              </dd>
            </div>

            <div>
              <dt>
                Fecha de nacimiento
              </dt>

              <dd>
                {formattedBirthDate}
              </dd>
            </div>

            <div>
              <dt>
                Estado
              </dt>

              <dd>
                <EstudianteEstadoBadge
                  estado={
                    student.estado
                  }
                />
              </dd>
            </div>
          </dl>
        </article>

        <article className="module-card">
          <header className="detail-card-header">
            <Phone
              size={19}
              aria-hidden="true"
            />

            <div>
              <h2>
                Contacto
              </h2>

              <p>
                Información de
                comunicación.
              </p>
            </div>
          </header>

          <div className="student-contact-list">
            <div>
              <Phone
                size={16}
                aria-hidden="true"
              />

              <span>
                {student.telefono ??
                  'Sin teléfono'}
              </span>
            </div>

            <div>
              <MessageCircle
                size={16}
                aria-hidden="true"
              />

              <span>
                {student.whatsapp ??
                  'Sin WhatsApp'}
              </span>
            </div>

            <div>
              <Mail
                size={16}
                aria-hidden="true"
              />

              <span>
                {student.email ??
                  'Sin correo electrónico'}
              </span>
            </div>

            <div>
              <MapPin
                size={16}
                aria-hidden="true"
              />

              <span>
                {student.direccion ??
                  'Sin dirección'}
              </span>
            </div>
          </div>
        </article>

        <article className="module-card student-audit-card">
          <header className="detail-card-header">
            <CalendarDays
              size={19}
              aria-hidden="true"
            />

            <div>
              <h2>
                Registro
              </h2>

              <p>
                Información del registro
                en el sistema.
              </p>
            </div>
          </header>

          <dl className="student-detail-list">
            <div>
              <dt>
                Creado
              </dt>

              <dd>
                {new Intl.DateTimeFormat(
                  'es-GT',
                  {
                    dateStyle:
                      'medium',
                    timeStyle:
                      'short',
                  },
                ).format(
                  new Date(
                    student.creado_en,
                  ),
                )}
              </dd>
            </div>

            <div>
              <dt>
                Última actualización
              </dt>

              <dd>
                {new Intl.DateTimeFormat(
                  'es-GT',
                  {
                    dateStyle:
                      'medium',
                    timeStyle:
                      'short',
                  },
                ).format(
                  new Date(
                    student.actualizado_en,
                  ),
                )}
              </dd>
            </div>
          </dl>
        </article>
      </section>

      {showEdit && (
        <EstudianteFormModal
          title="Editar estudiante"
          estudiante={student}
          isSubmitting={
            updateMutation.isPending
          }
          error={
            updateMutation.isError
              ? getApiErrorMessage(
                  updateMutation.error,
                  'No fue posible actualizar el estudiante.',
                )
              : null
          }
          onClose={() =>
            setShowEdit(false)
          }
          onSubmit={async (
            payload,
          ) => {
            await updateMutation.mutateAsync(
              payload,
            )
          }}
        />
      )}

      {showState && (
        <EstudianteEstadoModal
          estudiante={student}
          isSubmitting={
            stateMutation.isPending
          }
          error={
            stateMutation.isError
              ? getApiErrorMessage(
                  stateMutation.error,
                  'No fue posible cambiar el estado.',
                )
              : null
          }
          onClose={() =>
            setShowState(false)
          }
          onSubmit={async (
            nextState,
          ) => {
            await stateMutation.mutateAsync(
              nextState,
            )
          }}
        />
      )}
    </main>
  )
}

export default StudentDetailPage