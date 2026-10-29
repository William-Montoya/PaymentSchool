import {
  ChevronLeft,
  ChevronRight,
  Eye,
  Search,
  UserPlus,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  useNavigate,
} from 'react-router-dom'

import {
  createEstudiante,
  getEstudiantes,
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

import EstudianteFormModal from
  '../components/estudiantes/EstudianteFormModal'

import type {
  EstadoEstudiante,
  EstudianteCreate,
} from '../types/estudiante'

const PAGE_SIZE = 20

function StudentsPage() {
  const navigate =
    useNavigate()

  const queryClient =
    useQueryClient()

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
    estado,
    setEstado,
  ] =
    useState<
      EstadoEstudiante | ''
    >('')

  const [
    offset,
    setOffset,
  ] =
    useState(0)

  const [
    showCreate,
    setShowCreate,
  ] =
    useState(false)

  const studentsQuery =
    useQuery({
      queryKey: [
        'estudiantes',
        offset,
        estado,
        search,
      ],

      queryFn: () =>
        getEstudiantes({
          offset,
          limit: PAGE_SIZE,
          estado:
            estado || undefined,
          buscar:
            search || undefined,
        }),
    })

  const createMutation =
    useMutation({
      mutationFn:
        createEstudiante,

      onSuccess: async (
        estudiante,
      ) => {
        await queryClient.invalidateQueries({
          queryKey: [
            'estudiantes',
          ],
        })

        setShowCreate(false)

        navigate(
          `/estudiantes/${estudiante.id_estudiante}`,
        )
      },
    })

  function handleSearch(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setOffset(0)

    setSearch(
      searchDraft.trim(),
    )
  }

  async function handleCreate(
    payload: EstudianteCreate,
  ) {
    await createMutation.mutateAsync(
      payload,
    )
  }

  const students =
    studentsQuery.data ?? []

  return (
    <main className="module-page">
      <header className="module-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Gestión académica
          </span>

          <h1>
            Estudiantes
          </h1>

          <p>
            Consulta y administración
            de estudiantes.
          </p>
        </div>

        <PermissionGate
          anyOf={[
            PERMISSIONS
              .ESTUDIANTES_GESTIONAR,
          ]}
        >
          <button
            className="button button-primary"
            type="button"
            onClick={() =>
              setShowCreate(true)
            }
          >
            <UserPlus
              size={17}
              aria-hidden="true"
            />

            Nuevo estudiante
          </button>
        </PermissionGate>
      </header>

      <section className="module-card">
        <div className="student-toolbar">
          <form
            className="student-search"
            onSubmit={handleSearch}
          >
            <Search
              size={18}
              aria-hidden="true"
            />

            <input
              type="search"
              placeholder={
                'Buscar por código, nombre...'
              }
              value={searchDraft}
              onChange={(event) =>
                setSearchDraft(
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

          <select
            className="student-filter"
            value={estado}
            aria-label="Filtrar por estado"
            onChange={(event) => {
              setOffset(0)

              setEstado(
                event.target
                  .value as
                    | EstadoEstudiante
                    | '',
              )
            }}
          >
            <option value="">
              Todos los estados
            </option>

            <option value="ACTIVO">
              Activos
            </option>

            <option value="INACTIVO">
              Inactivos
            </option>

            <option value="RETIRADO">
              Retirados
            </option>

            <option value="EGRESADO">
              Egresados
            </option>
          </select>
        </div>

        {studentsQuery.isError ? (
          <div className="module-message module-message-error">
            <p>
              {getApiErrorMessage(
                studentsQuery.error,
                'No fue posible cargar los estudiantes.',
              )}
            </p>

            <button
              className="button button-secondary"
              type="button"
              onClick={() => {
                void studentsQuery.refetch()
              }}
            >
              Reintentar
            </button>
          </div>
        ) : studentsQuery.isLoading ? (
          <div className="module-message">
            Cargando estudiantes...
          </div>
        ) : students.length === 0 ? (
          <div className="module-message">
            No se encontraron estudiantes
            con los filtros seleccionados.
          </div>
        ) : (
          <div className="module-table-wrapper">
            <table className="module-table">
              <thead>
                <tr>
                  <th>
                    Código
                  </th>

                  <th>
                    Estudiante
                  </th>

                  <th>
                    Contacto
                  </th>

                  <th>
                    Estado
                  </th>

                  <th className="table-action-column">
                    Acción
                  </th>
                </tr>
              </thead>

              <tbody>
                {students.map(
                  (student) => (
                    <tr
                      key={
                        student.id_estudiante
                      }
                    >
                      <td>
                        <span className="student-code">
                          {
                            student.codigo_estudiante
                          }
                        </span>
                      </td>

                      <td>
                        <div className="student-name-cell">
                          <div className="student-avatar">
                            {student.nombres
                              .charAt(0)
                              .toUpperCase()}

                            {student.apellidos
                              .charAt(0)
                              .toUpperCase()}
                          </div>

                          <div>
                            <strong>
                              {student.nombres}
                              {' '}
                              {student.apellidos}
                            </strong>

                            <span>
                              {student.cui
                                ? `CUI ${student.cui}`
                                : 'Sin CUI registrado'}
                            </span>
                          </div>
                        </div>
                      </td>

                      <td>
                        <div className="student-contact-cell">
                          <span>
                            {student.email ??
                              'Sin correo'}
                          </span>

                          <small>
                            {student.telefono ??
                              student.whatsapp ??
                              'Sin teléfono'}
                          </small>
                        </div>
                      </td>

                      <td>
                        <EstudianteEstadoBadge
                          estado={
                            student.estado
                          }
                        />
                      </td>

                      <td className="table-action-column">
                        <button
                          className="table-icon-button"
                          type="button"
                          title="Ver estudiante"
                          aria-label="Ver estudiante"
                          onClick={() =>
                            navigate(
                              `/estudiantes/${student.id_estudiante}`,
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

        <footer className="module-pagination">
          <span>
            Mostrando
            {' '}
            {students.length}
            {' '}
            registros
          </span>

          <div>
            <button
              type="button"
              disabled={
                offset === 0
              }
              onClick={() =>
                setOffset(
                  (current) =>
                    Math.max(
                      0,
                      current -
                        PAGE_SIZE,
                    ),
                )
              }
              aria-label="Página anterior"
            >
              <ChevronLeft
                size={17}
                aria-hidden="true"
              />
            </button>

            <span>
              Página
              {' '}
              {Math.floor(
                offset /
                  PAGE_SIZE,
              ) + 1}
            </span>

            <button
              type="button"
              disabled={
                students.length <
                PAGE_SIZE
              }
              onClick={() =>
                setOffset(
                  (current) =>
                    current +
                    PAGE_SIZE,
                )
              }
              aria-label="Página siguiente"
            >
              <ChevronRight
                size={17}
                aria-hidden="true"
              />
            </button>
          </div>
        </footer>
      </section>

      {showCreate && (
        <EstudianteFormModal
          title="Nuevo estudiante"
          isSubmitting={
            createMutation.isPending
          }
          error={
            createMutation.isError
              ? getApiErrorMessage(
                  createMutation.error,
                  'No fue posible crear el estudiante.',
                )
              : null
          }
          onClose={() =>
            setShowCreate(false)
          }
          onSubmit={handleCreate}
        />
      )}
    </main>
  )
}

export default StudentsPage